from flask import jsonify, request
from app import es


def search_article():
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
