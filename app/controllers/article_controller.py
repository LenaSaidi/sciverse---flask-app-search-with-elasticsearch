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
from elasticsearch import Elasticsearch, NotFoundError
from app import es


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
    data = request.json
    current_date = datetime.utcnow()  # Utilisez datetime.now() si vous préférez l'heure locale

    new_article = Article(
        title=data.get('title'),
        abstract=data.get('abstract'),
        full_text=data.get('full_text'),
        pdf_url=data.get('pdf_url'),
        date=current_date
    )
    db.session.add(new_article)
    db.session.flush()

    for author_data in data.get('authors', []):
        author = Author(
            name=author_data.get('name'),
            email=author_data.get('email')
        )
        db.session.add(author)
        db.session.flush()

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

    try:
        db.session.commit()
        
        # Si la base de données est mise à jour avec succès, essayez d'indexer l'article dans Elasticsearch
        try:
            response = es.index(index='articles_index', body={
                "title": data.get('title', ''),
                "abstract": data.get('abstract', ''),
                "full_text": data.get('full_text', ''),
                "keywords": data.get('keywords', []),
                "pdf_url": data.get('pdf_url', ''),
                "references": data.get('references', []),
                "date": data.get('date', ''),
                "authors": data.get('authors', []),
                "institution_names": [inst.get('institution_name', '') for author in data.get('authors', []) for inst in author.get('institutions', []) if inst.get('institution_name', '')]
                # Vous pouvez ajouter d'autres champs si nécessaire
            })
            elasticsearch_id = response['_id']

            # Ajoutez une entrée dans la table de correspondance
            mapping_entry = ArticleElasticsearchMapping(article_id=new_article.id, elasticsearch_id=elasticsearch_id)
            db.session.add(mapping_entry)
            db.session.commit()
            return jsonify({"message": "Article added and indexed successfully!"}), 201
        except Exception as es_error:
            # Si l'indexation dans Elasticsearch échoue, faites un rollback de la transaction de la base de données
            db.session.rollback()
            return jsonify({"error": f"Failed to index the article in Elasticsearch: {str(es_error)}"}), 500

    except Exception as db_error:
        # Si la mise à jour de la base de données échoue, renvoyez une erreur appropriée
        db.session.rollback()
        return jsonify({'error': f"Failed to add the article to the database: {str(db_error)}"}), 500

#get articles with fav of a specific user
@jwt_required()
def get_articles():
    try:
        # Get the user ID from the JWT token
        user_id = get_jwt_identity()

        # Query the user
        user = User.query.get(user_id)

        # Query all articles with favorite information
        articles = Article.query.all()

        # Create a response containing articles with a boolean indicating if it's a favorite
        response_articles = [
            {
                'id': article.id,
                'title': article.title,
                'content': article.content,
               'is_favorite': article in user.favorite_articles
            }
            for article in articles
        ]

        return jsonify({'articles': response_articles}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

#get all articles of db without fav
@jwt_required()
def get_all_articles():
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
        return jsonify({'error': 'Article not found!'}), 404

    try:
        db.session.delete(article)
        ArticleEdit.query.filter_by(article_id=article.id).delete()
       #FavoriteArticle.query.filter_by(article_id=article.id).delete()
        db.session.commit()
        return jsonify({'message': 'Article and associated data deleted successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    

@jwt_required()
def get_article_from_elasticsearch(article_id):
    try:
        # Recherchez l'ID Elasticsearch associé à l'article_id dans la table de mappage
        mapping_entry = ArticleElasticsearchMapping.query.filter_by(article_id=article_id).first()

        if not mapping_entry:
            return jsonify({'error': f'Mapping entry not found for article ID {article_id}'}), 404

        # Récupérez l'elasticsearch_id de l'entrée de mappage
        elasticsearch_id = mapping_entry.elasticsearch_id

        # Recherchez l'article dans Elasticsearch en utilisant l'elasticsearch_id
        response = es.get(index="articles_index", id=elasticsearch_id)
        article_data = response["_source"]

        # Formatez la réponse selon vos besoins
        formatted_response = {
            'id': article_id,
            'title': article_data['title'],
            'abstract': article_data['abstract'],
            'full_text': article_data['full_text'],
            'keywords': article_data['keywords'],
            'pdf_url': article_data['pdf_url'],
            'references': article_data['references'],
            'date': article_data['date'],
            'authors': article_data['authors'],
            'institution_names': article_data['institution_names']
        }

        return jsonify({'article': formatted_response}), 200

    except NotFoundError:
        return jsonify({'error': f'Article not found in Elasticsearch with ID {elasticsearch_id}'}), 404

    except Exception as e:
        return jsonify({'error': f'Error retrieving article: {str(e)}'}), 500

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
    
