import elasticsearch
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import es
from app.models import ArticleElasticsearchMapping, FavoriteArticle

@jwt_required()
def search_article():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    # Récupérer les articles favoris de l'utilisateur
    favorite_articles = FavoriteArticle.query.filter_by(user_id=current_user_id).all()
    favorite_article_ids = set([fav.article_id for fav in favorite_articles])
    
    if not data or 'queries' not in data:
        return jsonify({"error": "Invalid request data."}), 400

    queries = data['queries']
    must_conditions = []

    # Pour chaque terme et champ spécifié par l'utilisateur
    for query in queries:
        term = query.get('term')
        field = query.get('field')
        # Si le champ est "authors", nous devons traiter cela différemment
        if field == 'authors':
            # Recherchez le terme dans les noms des auteurs et les noms des institutions
            must_conditions.append({
                'bool': {
                    'should': [
                        {'match': {'authors.name': term}},
                        {'match': {'authors.institutions.institution_name': term}}
                    ]
                }
            })
        else:
            # Si ce n'est pas "authors"
            must_conditions.append({
                'multi_match': {
                    'query': term,
                    'fields': [field]
                }
            })

    try:
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
                article = hit['_source']
                elasticsearch_id = hit['_id']
                mapping_entry = ArticleElasticsearchMapping.query.filter_by(elasticsearch_id=elasticsearch_id).first()
                article_id = mapping_entry.article_id

                # Vérifiez si l'article est un favori de l'utilisateur
                is_favorite = article_id in favorite_article_ids
                
                # Ajoutez une clé is_favorite à chaque article
                article['is_favorite'] = is_favorite
                
                # Ajoutez l'article à la liste
                articles_data.append(article)

            return jsonify({"articles": articles_data}), 200
        else:
            return jsonify({"message": "No articles found matching the specified criteria."}), 404

    except Exception as e:
        return jsonify({"error": f"Search failed: {str(e)}"}), 500
    

