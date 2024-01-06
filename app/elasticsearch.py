from flask import jsonify, request
from app import es

def search_article():
    data = request.get_json()

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
            articles_data = [hit['_source'] for hit in hits]
            return jsonify({"articles": articles_data}), 200
        else:
            return jsonify({"message": "No articles found matching the specified criteria."}), 404
    except Exception as e:
        return jsonify({"error": f"Search failed: {str(e)}"}), 500
    

def search_article2():
    data = request.get_json()
    if not data or 'search_term' not in data:
        return jsonify({"error": "Invalid request data."}), 400

    search_term = data['search_term']
    fields_to_search = data.get('fields')

    # Vérifiez si les champs de recherche sont spécifiés à "all"
    if fields_to_search == "all":
        fields_to_search = ['title', 'abstract', 'full_text', 'keywords', 'references', 'date', 'authors', 'institution_names']
    
    try:
        response = es.search(index='articles_index', body={
            'query': {
                'multi_match': {
                    'query': search_term,
                    'fields': fields_to_search
                }
            }
        })

        hits = response['hits']['hits']
        
        if hits:
            # Récupérez directement le contenu des documents correspondants
            articles_data = [hit['_source'] for hit in hits]
            
            return jsonify({"articles": articles_data}), 200
        else:
            return jsonify({"message": f"The term '{search_term}' was not found in the specified fields."}), 404
    except Exception as e:
        return jsonify({"error": f"Search failed: {str(e)}"}), 500
