# # app/controllers/pdf_controller.py

# from flask import jsonify, request, current_app
# from flask_jwt_extended import jwt_required
# from werkzeug.security import generate_password_hash, check_password_hash
# from app import db
# from app.models import Article
# from app import grobid_client
# from werkzeug.utils import secure_filename

# ALLOWED_EXTENSIONS = {'pdf'}
# GROBID_OUTPUT_FORMAT = 'json'

# # Helper function to check allowed file extensions
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @jwt_required()
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400

#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400

#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
#         file.save(filepath)

#         # Process PDF with GROBID
#         try:
#             response = grobid_client.process(filepath, GROBID_OUTPUT_FORMAT)
#             # Assuming GROBID response is JSON format
#             json_data = response.json()
#             # Store JSON data in database
#             save_to_database(json_data)
#             return jsonify({'message': 'PDF processed successfully'}), 200
#         except grobid_client.GrobidException as e:
#             return jsonify({'error': f'Failed to process PDF: {str(e)}'}), 500
#         except Exception as e:
#             return jsonify({'error': f'An error occurred: {str(e)}'}), 500

#     return jsonify({'error': 'Invalid file format'}), 400

# def save_to_database(json_data):
#     # Example: Save JSON data to the Article table in your database
#     article = Article(title=json_data.get('title', ''),
#                       abstract=json_data.get('abstract', ''))
#     db.session.add(article)
#     db.session.commit()