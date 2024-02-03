# app/controllers/pdf_controller.py
from flask import Flask, request, jsonify
from flask_jwt_extended import current_user, get_jwt_identity, jwt_required
from flask_jwt_extended import jwt_required, unset_jwt_cookies
from flask_login import login_manager, LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import ForeignKey
from app.models import Article, ArticleAuthor, ArticleElasticsearchMapping, ArticleKeyword, ArticleReference, Author, AuthorInstitution, BibliographicReference, Institution, Keyword, User
from app import db
from app import login_manager
from elasticsearch import Elasticsearch, NotFoundError
from app import es
from JsonGnr import JsonGenr
from datetime import datetime
import requests
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
# import re




def generate_unique_filename(prefix, extension):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{prefix}_{timestamp}.{extension}"
    return filename



def add_article():
    pdf_url = request.json.get('pdf_url')
    if not pdf_url:
        return jsonify({'error': 'PDF URL is missing'}), 400
    
    file_name = generate_unique_filename('article', 'pdf')
    # file_name = 'article9.pdf'
    try:
        download_pdf_from_url(pdf_url, file_name)
        # Return the response here
        response = jsonify({'message': 'PDF downloaded successfully'}), 200  
    except Exception as e:
        return jsonify({'error': f"Failed to download PDF: {str(e)}"}), 500
    
    try:
        article_name, extension = os.path.splitext(file_name)
        # article_name = 'article9'
        pdf_grobid_path = 'grobid_client_python/tests/test_pdf'
        json_data = JsonGenr(pdf_grobid_path,article_name)
        response = jsonify({'message': 'PDF processed successfully'}), 200
        
        # Create and add the article to the database
        new_article = Article(
            title=json_data.get('title', ''),
            abstract=json_data.get('abstract', ''),
            full_text=json_data.get('full_text', ''),
            pdf_url=pdf_url,
            date=datetime.utcnow()  # Utilize datetime.now() if you prefer the local time
        )
        db.session.add(new_article)
        db.session.flush()

        # Add authors and their institutions
        for author_data in json_data['authors']:
            author = Author(
                name=author_data['name'],
                email=author_data['email']
            )
            db.session.add(author)
            db.session.flush()

            for institution_info in author_data['institutions']:
                institution = Institution(institution_name=institution_info['institution_name'])
                db.session.add(institution)
                db.session.flush()

                author_institution = AuthorInstitution(author_id=author.id, institution_id=institution.id)
                db.session.add(author_institution)

            relation = ArticleAuthor(article_id=new_article.id, author_id=author.id)
            db.session.add(relation)

        # Add keywords
        for keyword_data in json_data['keywords']:
            keyword = Keyword(keyword=keyword_data)
            db.session.add(keyword)
            db.session.flush()

            relation = ArticleKeyword(article_id=new_article.id, keyword_id=keyword.id)
            db.session.add(relation)

        # Add references
        for reference_data in json_data['references']:
            reference = BibliographicReference(reference=reference_data)
            db.session.add(reference)
            db.session.flush()

            relation = ArticleReference(article_id=new_article.id, reference_id=reference.id)
            db.session.add(relation)

        db.session.commit()

        # Index the article in Elasticsearch
        response = es.index(index='articles_index', body={
            "title": json_data.get('title', ''),
            "abstract": json_data.get('abstract', ''),
            "full_text": json_data.get('full_text', ''),
            "keywords": json_data.get('keywords', []),
            "pdf_url": json_data.get('pdf_url', ''),
            "references": json_data.get('references', []),
            "date": json_data.get('date', ''),
            "authors": json_data.get('authors', []),
            "institution_names": [inst.get('institution_name', '') for author in json_data.get('authors', []) for inst in author.get('institutions', []) if inst.get('institution_name', '')]
            # You can add other fields if necessary
        })
        elasticsearch_id = response['_id']

        # Add an entry in the mapping table
        mapping_entry = ArticleElasticsearchMapping(article_id=new_article.id, elasticsearch_id=elasticsearch_id)
        db.session.add(mapping_entry)
        db.session.commit()

        return jsonify({"message": "Article added and indexed successfully!"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Failed to process PDF with GROBID or add the article to the database: {str(e)}"}), 500




    




def download_pdf_from_url(url, file_name):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_directory = os.path.abspath(os.path.join(current_dir, '..', '..', 'grobid_client_python', 'tests', 'test_pdf'))
        os.makedirs(pdf_directory, exist_ok=True)
        save_path = os.path.join(pdf_directory, file_name)

        # Send a GET request to the URL to retrieve the content
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Open a file in binary write mode to save the PDF content
        with open(save_path, 'wb') as pdf_file:
            # Iterate over the content in chunks and write to the file
            for chunk in response.iter_content(chunk_size=8192):
                pdf_file.write(chunk)

        print(f"PDF downloaded successfully and saved at: {save_path}")
        return True
    except Exception as e:
        print(f"Failed to download PDF: {e}")
        return False





def generate_pdf(article):
    
    new_pdf_filename = f'article_{article.id}.pdf'
    # new_pdf_path = os.path.join('controller/pdfs', new_pdf_filename)
    # Define the directory where the PDFs will be stored relative to the current file

    pdf_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pdfs'))

    # Ensure the directory exists, create it if it doesn't
    os.makedirs(pdf_directory, exist_ok=True)

    # Define the full path to the new PDF file
    new_pdf_path = os.path.join(pdf_directory, new_pdf_filename)
    
    # Create a new PDF file
    pdf = canvas.Canvas(new_pdf_path, pagesize=letter)
    pdf.setTitle(article.title)
    pdf.drawString(100, 750, f"Title: {article.title}")
    pdf.drawString(100, 730, f"Abstract: {article.abstract}")
    pdf.drawString(100, 710, f"Full Text: {article.full_text}")
    pdf.drawString(100, 690, f"PDF URL: {article.pdf_url}")
    pdf.drawString(100, 670, f"Date: {article.date}")
    pdf.drawString(100, 650, "Authors:")
    y = 630
    for author in article.authors:
        pdf.drawString(120, y, f"Name: {author.name}")
        pdf.drawString(120, y - 20, f"Email: {author.email}")
        y -= 40
    pdf.drawString(100, 610, "Keywords:")
    y = 590
    for keyword in article.keywords:
        pdf.drawString(120, y, f"{keyword.keyword}")
        y -= 20
    pdf.drawString(100, 570, "References:")
    y = 550
    for reference in article.references:
        pdf.drawString(120, y, f"{reference.reference}")
        y -= 20
    pdf.save()
    return new_pdf_path



