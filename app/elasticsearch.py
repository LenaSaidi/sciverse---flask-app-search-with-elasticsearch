from flask import jsonify, request
from app import es
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User
from app.models import Article
from app.models import ArticleElasticsearchMapping



@jwt_required()
def search_article():
    data = request.get_json()

    if not data or 'queries' not in data:
        return jsonify({"error": "Invalid request data."}), 400

    queries = data['queries']
    must_conditions = []

    # For each term and field specified by the user
    for query in queries:
        term = query.get('term')
        field = query.get('field')
        # If the field is "authors", we need to handle it differently
        if field == 'authors':
            # Search for the term in author names and institution names
            must_conditions.append({
                'bool': {
                    'should': [
                        {'match': {'authors.name': term}},
                        {'match': {'authors.institutions.institution_name': term}}
                    ]
                }
            })
        else:
            # If it's not "authors"
            must_conditions.append({
                'multi_match': {
                    'query': term,
                    'fields': [field]
                }
            })

    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        # Get IDs of favorite articles for the user
        favorite_article_ids = {article.id for article in user.favorite_articles}

        response = es.search(index='articles_index', body={
            'query': {
                'bool': {
                    'must': must_conditions
                }
            }
        })

        hits = response['hits']['hits']

        if hits:
            articles_data = []
            for hit in hits:
                article_source = hit['_source']
                article_id = hit['_id']
                # Fetch article ID from your database
                db_article_id = get_db_article_id(article_id)
                if db_article_id:
                    # Check if the article is a favorite
                    is_favorite = db_article_id in favorite_article_ids
                    article_data = {
                        'db_id': db_article_id,
                        'es_id': article_id,
                        'is_favorite': is_favorite,
                        **article_source
                    }
                    articles_data.append(article_data)
            return jsonify({"articles": articles_data}), 200
        else:
            return jsonify({"message": "No articles found matching the specified criteria."}), 404
    except Exception as e:
        return jsonify({"error": f"Search failed: {str(e)}"}), 500

def get_db_article_id(es_id):
    # Implement logic to retrieve article ID from your database based on Elasticsearch ID
    # This could involve querying your database or using a mapping between Elasticsearch and database IDs
    # For simplicity, let's assume a direct mapping for now
    mapping_entry = ArticleElasticsearchMapping.query.filter_by(elasticsearch_id=es_id).first()
    if mapping_entry:
        return mapping_entry.article_id
    else:
        return None
