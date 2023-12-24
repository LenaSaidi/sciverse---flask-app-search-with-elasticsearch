from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import ForeignKey
from app.models import *


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
        return jsonify({'message': 'Article added successfully!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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