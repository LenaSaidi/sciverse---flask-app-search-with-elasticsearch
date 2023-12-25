from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import ForeignKey
from app.models import *
from elasticsearch import Elasticsearch
from app import es


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
    return jsonify(articles_list)
    

def delete_article(article_id):
    article = Article.query.get(article_id)

    if not article:
        return jsonify({'error': 'Article not found!'}), 404

    try:
        db.session.delete(article)
        db.session.commit()
        return jsonify({'message': 'Article and associated data deleted successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    # Retourner la liste des articles en format JSON
    return jsonify({'articles': articles_list})

def update_article(article_id):
    # Récupérer l'article par son ID
    article = Article.query.get(article_id)
    if not article:
        return jsonify({'error': 'Article not found!'}), 404

    # Extraire les données mises à jour du corps de la requête
    data = request.json

    # Mettre à jour les champs de l'article
    article.title = data.get('title', article.title)
    article.abstract = data.get('abstract', article.abstract)
    article.full_text = data.get('full_text', article.full_text)
    article.pdf_url = data.get('pdf_url', article.pdf_url)
    article.date = datetime.utcnow()

    # Mettre à jour les auteurs associés et leurs institutions
    if 'authors' in data:
        article.authors.clear()
        for author_data in data['authors']:
            email = author_data.get('email')
            author = Author.query.filter_by(email=email).first()
            if not author:
                author = Author(name=author_data['name'], email=email)
            
            # Mettre à jour ou créer l'institution associée à l'auteur
            for institution_data in author_data.get('institutions', []):
                institution_name = institution_data.get('institution_name')
                institution = Institution.query.filter_by(institution_name=institution_name).first()
                if not institution:
                    institution = Institution(institution_name=institution_name)
                # Vérifiez si l'institution n'est pas déjà associée à l'auteur
                if institution not in author.institutions:
                    author.institutions.append(institution)
            
            # Mettre à jour le nom de l'auteur si différent
            if author.name != author_data['name']:
                author.name = author_data['name']
            
            article.authors.append(author)

        # Mettre à jour les mots-clés
        if 'keywords' in data:
            article.keywords.clear()
            for keyword_data in data['keywords']:
                keyword = Keyword.query.filter_by(keyword=keyword_data).first() if keyword_data else None
                if not keyword:
                    keyword = Keyword(keyword=keyword_data)
                article.keywords.append(keyword)

    # Mettre à jour les références
    if 'references' in data:
        article.references.clear()
        for reference_data in data['references']:
            reference = BibliographicReference.query.filter_by(reference=reference_data).first() if reference_data else None
            if not reference:
                reference = BibliographicReference(reference=reference_data)
            article.references.append(reference)

    try:
        db.session.commit()
        return jsonify({'message': 'Article updated successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    

def get_article(id_article):

    # Recherche de l'article dans la base de données en fonction de son ID
    article = Article.query.get(id_article)
    
    if not article:
        return jsonify({'error': 'Article not found'}), 404

    # Liste pour stocker les données des auteurs associés à l'article
    auteurs_list = []
    
    # Parcourir la relation ArticleAuteur pour obtenir les auteurs de l'article
    for article_auteur_relation in article.authors:
        author = article_auteur_relation
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

    # Construire la réponse pour un article spécifique
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
    return jsonify(article_data), 200    
