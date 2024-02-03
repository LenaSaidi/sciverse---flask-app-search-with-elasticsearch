import os
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
# from JsonFrm import Json_ret
from JsonGnr import JsonGenr
import os
from datetime import datetime
import requests
import re

from app.controllers.pdf_controller import generate_pdf



# url = "https://drive.google.com/uc?export=download&id=1MMPyrC79eFmplgabBhrqpNi6QSVOHD1p"
# file_name = "article18.pdf"
# download_pdf(url, file_name)



    #------------------------------------ SQL  GET-------------------------------------


#get one article from sql
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

# get articles with fav of a specific user
# Get articles from SQL


#get articles with fav of a specific user
# Get articles from SQL
@jwt_required()
def get_articles():
    try:
        # Get the user ID from the JWT token
        user_id = get_jwt_identity()

        # Query the user
        user = User.query.get(user_id)

        # Query all articles with favorite information
        articles = Article.query.all()

        response_articles = []
        for article in articles:
            response_article = {
                'id': article.id,
                'title': article.title,
                'abstract': article.abstract,
                'full_text': article.full_text,
                'pdf_url': article.pdf_url,
                'authors': [],
                'keywords': [],
                'references': [],
                'is_favorite': article in user.favorite_articles,
                'date': article.date.isoformat()
            }

            # Check if keywords are stored as strings or Keyword model instances
            if isinstance(article.keywords[0], Keyword):
                # Extract keyword strings from Keyword model instances
                response_article['keywords'] = [keyword.keyword for keyword in article.keywords]
            else:
                # Keywords are already stored as strings
                response_article['keywords'] = article.keywords

            for author in article.authors:
                author_data = {
                    'id': author.id,
                    'name': author.name,
                    'email': author.email,
                    'institutions': [{'institution_name': institution.institution_name} for institution in author.institutions]
                }
                response_article['authors'].append(author_data)

            for reference in article.references:
                reference_data = {
                    'id': reference.id,
                    'reference': reference.reference
                }
                response_article['references'].append(reference_data)

            response_articles.append(response_article)

        return jsonify({'articles': response_articles}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


#get all articles from sql	
@jwt_required()
def get_all_articles():
    try:
        articles = Article.query.all()

        response_articles = [
            {
                'id': article.id,
                'title': article.title,
                'abstract': article.abstract,
                'full_text': article.full_text,
                'pdf_url': article.pdf_url,
                'authors': [{'id': author.id, 'name': author.name, 'email': author.email} for author in article.authors],
                'keywords': [{'id': keyword.id, 'keyword': keyword.keyword} for keyword in article.keywords],
                'references': [{'id': reference.id, 'reference': reference.reference} for reference in article.references],
                'date': article.date.isoformat()
            }
            for article in articles
        ]

        return jsonify({'articles': response_articles}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


    #------------------------------------ ADD PUT DELETE-------------------------------------


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
        # article.pdf_url = request.json.get('pdf_url', article.pdf_url)
    
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

        article.pdf_url = generate_pdf(article)
        # Save the updated article
        db.session.commit()

        mapping_entry = ArticleElasticsearchMapping.query.filter_by(article_id=article.id).first()
        if mapping_entry:
            elasticsearch_id = mapping_entry.elasticsearch_id
        # Update the corresponding Elasticsearch index
        try:
            # mapping_entry = ArticleElasticsearchMapping(article_id=new_article.id, elasticsearch_id=elasticsearch_id)
            es.update(index='articles_index', id=elasticsearch_id, body={
                "doc": {
                    "title": article.title,
                    "abstract": article.abstract,
                    "full_text": article.full_text,
                    "keywords": [keyword.keyword for keyword in article.keywords],
                    "pdf_url": article.pdf_url,
                    "references": [reference.reference for reference in article.references],
                    "date": article.date.strftime('%Y-%m-%dT%H:%M:%SZ'),  # Format date as per Elasticsearch
                    "authors": [{"name": author.name, "email": author.email} for author in article.authors],
                    "institution_names": [inst.institution_name for author in article.authors for inst in author.institutions]
                }
            })
        except Exception as es_error:
            return jsonify({"error": f"Failed to update the article in Elasticsearch: {str(es_error)}"}), 500

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
    





    #------------------------------------ EDITS ARTICLE-------------------------------------


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
    







    #------------------------------------ ELASTIC SEARCH GET-------------------------------------



#get one article from elastic search
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
def get_all_articles_from_elasticsearch():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        # Get IDs of favorite articles for the user
        favorite_article_ids = {article.id for article in user.favorite_articles}

        # Initialize variables for pagination
        page_size = 10  # Adjust as needed
        current_page = 1
        total_hits = float('inf')
        formatted_response = []

        while len(formatted_response) < total_hits:
            # Search documents in the Elasticsearch index with pagination
            response = es.search(index="articles_index", body={"query": {"match_all": {}}, "size": page_size, "from": (current_page - 1) * page_size})
            hits = response['hits']['hits']
            total_hits = response['hits']['total']['value']

            # Format the response with favorite status and article IDs
            for hit in hits:
                es_id = hit['_id']
                db_id = get_db_article_id(es_id)
                is_favorite = db_id in favorite_article_ids
                article_data = {
                    'es_id': es_id,
                    'db_id': db_id,
                    'is_favorite': is_favorite,
                    'title': hit['_source']['title'],
                    'abstract': hit['_source']['abstract'],
                    'full_text': hit['_source']['full_text'],
                    'keywords': hit['_source']['keywords'],
                    'pdf_url': hit['_source']['pdf_url'],
                    'references': hit['_source']['references'],
                    'date': hit['_source']['date'],
                    'authors': hit['_source']['authors'],
                    'institution_names': hit['_source']['institution_names']
                }
                formatted_response.append(article_data)

            # Move to the next page
            current_page += 1

        return jsonify({'articles': formatted_response}), 200

    except Exception as e:
        return jsonify({'error': f'Error retrieving articles: {str(e)}'}), 500

def get_db_article_id(es_id):
    # Implement logic to retrieve article ID from your database based on Elasticsearch ID
    # This could involve querying your database or using a mapping between Elasticsearch and database IDs
    # For simplicity, let's assume a direct mapping for now
    mapping_entry = ArticleElasticsearchMapping.query.filter_by(elasticsearch_id=es_id).first()
    if mapping_entry:
        return mapping_entry.article_id
    else:
        return None


