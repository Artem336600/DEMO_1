from flask import Blueprint, render_template, request, jsonify
from services.search_service import SearchService

main_bp = Blueprint('main', __name__)
search_service = SearchService()

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({
            'status': 'error',
            'message': 'Пустой запрос'
        }), 400
    
    # Perform search using the search service
    results = search_service.search(query)
    
    return jsonify({
        'status': 'success',
        'query': query,
        'results': results['results'],
        'total': results['total'],
        'processing_time': results['processing_time']
    })

@main_bp.route('/suggestions', methods=['GET'])
def get_suggestions():
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    suggestions = search_service.get_suggestions(query)
    return jsonify(suggestions)

@main_bp.route('/trending', methods=['GET'])
def get_trending():
    trending = search_service.get_trending_searches()
    return jsonify(trending) 