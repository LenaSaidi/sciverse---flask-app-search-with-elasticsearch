from flask import Flask, request, jsonify
from flask_jwt_extended import current_user, get_jwt_identity
from flask_jwt_extended import jwt_required, unset_jwt_cookies
from flask_login import login_manager, LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import ForeignKey
from app.models import *
from app import db
from app import login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#get article
@jwt_required()
def get_article(article_id):
    article = Article.query.get(article_id)

    if not article:
        return jsonify({'error': 'Article not found'}), 404

    # Example: Extracting author details 
    authors = [{'id': author.id, 'name': author.name, 'email': author.email} for author in article.authors]

    # Example: Extracting keyword details 
    keywords = [{'id': keyword.id, 'keyword': keyword.keyword} for keyword in article.keywords]

    # Example: Extracting reference details
    references = [{'id': reference.id, 'reference': reference.reference} for reference in article.references]

    article_data = {
        'id': article.id,
        'title': article.title,
        'abstract': article.abstract,
        'full_text': article.full_text,
        'pdf_url': article.pdf_url,
        'date': article.date.isoformat(),
        'authors': authors,
        'keywords': keywords,
        'references': references
    }

    return jsonify({'article': article_data})


#add article
@jwt_required()
def add_article():
    try:
        data = request.json
        if not isinstance(data, dict):
            raise ValueError("Invalid JSON data. Expected a dictionary.")
        
        current_date = datetime.utcnow()

        new_article = Article(
            title=data.get('title'),
            abstract=data.get('abstract'),
            full_text=data.get('full_text'),
            pdf_url=data.get('pdf_url'),
            date=current_date
        )
        db.session.add(new_article)
        db.session.flush()

        # Simplified data extraction for authors
        authors_data = data.get('authors', [])
        for author_data in authors_data:
            name = author_data.get('name')
            email = author_data.get('email')

            # Check if the author already exists
            author = Author.query.filter_by(email=email).first()
            if not author:
                author = Author(name=name, email=email)
                db.session.add(author)
                try:
                    db.session.flush()
                except Exception as e:
                    db.session.rollback()


            relation = ArticleAuthor(article_id=new_article.id, author_id=author.id)
            db.session.add(relation)

            for institution_data in author_data.get('institutions', []):
                institution = Institution(institution_name=institution_data.get('institution_name'))
                db.session.add(institution)
                db.session.flush()

                author_institution = AuthorInstitution(author_id=author.id, institution_id=institution.id)
                db.session.add(author_institution)

        for keyword_data in data.get('keywords', []):
            keyword = Keyword(keyword=keyword_data)
            db.session.add(keyword)
            db.session.flush()

            relation = ArticleKeyword(article_id=new_article.id, keyword_id=keyword.id)
            db.session.add(relation)

        for reference_data in data.get('references', []):
            reference = BibliographicReference(reference=reference_data)
            db.session.add(reference)
            db.session.flush()

            relation = ArticleReference(article_id=new_article.id, reference_id=reference.id)
            db.session.add(relation)

        db.session.commit()
        return jsonify({'message': 'Article added successfully!'}), 201
    except ValueError as ve:
        db.session.rollback()
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



#get articles
@jwt_required()
def get_articles():
    # Récupérer tous les articles depuis la base de données
    articles = Article.query.all()

    articles_list = []
    for article in articles:
        # Liste pour stocker les données des auteurs associés à l'article
        auteurs_list = []
        
        # Parcourir la relation ArticleAuteur pour obtenir les auteurs de l'article
        for article_auteur_relation in article.authors:
            author = article_auteur_relation  # Ici, il n'est pas nécessaire d'obtenir l'objet Auteur à partir de la relation, car elle est directe
            auteur_data = {
                'name': author.name,
                'email': author.email,
                'institutions': [{"institution_name": institution.institution_name} for institution in author.institutions]
            }
            auteurs_list.append(auteur_data)

        # Récupérer les mots-clés associés à l'article
        keywords = [keyword.keyword for keyword in article.keywords]

        # Récupérer les références associées à l'article
        references_list = [ref.reference for ref in article.references]

        # Construire la réponse pour un article
        article_data = {
            'id': article.id,
            'title': article.title,
            'abstract': article.abstract,
            'full_text': article.full_text,
            'pdf_url': article.pdf_url,
            'date': article.date,
            'keywords': keywords,
            'authors': auteurs_list,
            'references': references_list
        }

        articles_list.append(article_data)

    # Retourner la liste des articles en format JSON
    return jsonify({'articles': articles_list})



# Edit Article

@jwt_required()
def edit_article(article_id):
    article = Article.query.get(article_id)

    if not article:
        return jsonify({'error': 'Article not found'}), 404
    
    current_user_id = get_jwt_identity()


    if request.method == 'PUT':
        # Update the article fields
        article.title = request.json.get('title', article.title)
        article.abstract = request.json.get('abstract', article.abstract)
        article.full_text = request.json.get('full_text', article.full_text)
        article.pdf_url = request.json.get('pdf_url', article.pdf_url)

        # Update other attributes
        article.references = []

        for reference_data in request.json.get('references', []):
            reference = BibliographicReference.query.filter_by(reference=reference_data).first()

            if not reference:
                # Create a new reference if not exists
                reference = BibliographicReference(reference=reference_data)
                db.session.add(reference)

            article.references.append(reference)

        article.keywords = []

        for keyword_data in request.json.get('keywords', []):
            keyword = Keyword.query.filter_by(keyword=keyword_data).first()

            if not keyword:
                # Create a new keyword if not exists
                keyword = Keyword(keyword=keyword_data)
                db.session.add(keyword)

            article.keywords.append(keyword)

        # Update authors
        updated_authors = request.json.get('authors', [])
        article.authors = []

        for author_data in updated_authors:
            author = Author.query.filter_by(email=author_data['email']).first()

            if not author:
                # Create a new author if not exists
                author = Author(name=author_data['name'], email=author_data['email'])
                db.session.add(author)

            article.authors.append(author)

        # Save the updated article
        db.session.commit()

        # Create a new ArticleEdit record
        edit = ArticleEdit(
            article_id=article.id,
            user_id=current_user_id,
            edited_at=datetime.utcnow()
        )
        db.session.add(edit)
        db.session.commit()

        return jsonify({'message': 'Article edited successfully'})


#delete article 
    
@jwt_required()
def delete_article(article_id):
    article = Article.query.get(article_id)

    if not article:
        return jsonify({'error': 'Article not found'}), 404

    if current_user != article.author:
        return jsonify({'error': 'Forbidden'}), 403

    # Delete the article and its associated records (e.g., ArticleEdits, Favorites)
    ArticleEdit.query.filter_by(article_id=article.id).delete()
    FavoriteArticle.query.filter_by(article_id=article.id).delete()
    db.session.delete(article)
    db.session.commit()

    return jsonify({'message': 'Article deleted successfully'})

@jwt_required()
def get_article_edits(article_id):
    article = Article.query.get(article_id)

    if not article:
        return jsonify({'error': 'Article not found'}), 404

    # Get all edits associated with the article
    edits = ArticleEdit.query.filter_by(article_id=article.id).all()

    # Format edits data
    edits_data = []
    for edit in edits:
        edit_data = {
            'id': edit.id,
            'user_id': edit.user_id,
            'edited_at': edit.edited_at.isoformat(),
        }
        edits_data.append(edit_data)

    return jsonify({'edits': edits_data})
    
