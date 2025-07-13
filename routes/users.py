from flask import Blueprint, render_template, request, jsonify
from database import db

users = Blueprint('users', __name__, url_prefix='/users')

@users.route('/')
def users_list():
    """Список всех пользователей"""
    user_type = request.args.get('type')
    faculty = request.args.get('faculty')
    query = request.args.get('q')
    
    users_data = db.search_users(
        query=query,
        faculty=faculty,
        user_type=user_type,
        limit=50
    )
    
    # Получение статистики
    stats = db.get_user_type_statistics()
    
    return render_template('users/list.html', 
                         users=users_data, 
                         stats=stats,
                         current_filters={
                             'type': user_type,
                             'faculty': faculty,
                             'query': query
                         })

@users.route('/type/<user_type>')
def users_by_type(user_type):
    """Пользователи определенного типа"""
    users_data = db.get_users_by_type(user_type, limit=50)
    type_description = db.get_user_type_description(user_type)
    
    return render_template('users/by_type.html', 
                         users=users_data, 
                         user_type=user_type,
                         type_description=type_description)

@users.route('/profile/<user_id>')
def user_profile(user_id):
    """Профиль пользователя"""
    user = db.get_user_by_id(user_id)
    
    if not user:
        return render_template('errors/404.html'), 404
    
    # Получение дополнительных данных в зависимости от типа
    additional_data = None
    purpose = user.get('purpose')
    
    if purpose == 'find_people':
        additional_data = db.get_users_with_purpose_data('find_people', limit=1)
        additional_data = additional_data[0] if additional_data else None
    elif purpose == 'join_project':
        additional_data = db.get_users_with_purpose_data('join_project', limit=1)
        additional_data = additional_data[0] if additional_data else None
    elif purpose == 'expand_network':
        additional_data = db.get_users_with_purpose_data('expand_network', limit=1)
        additional_data = additional_data[0] if additional_data else None
    
    return render_template('users/profile.html', 
                         user=user, 
                         additional_data=additional_data)

@users.route('/api/stats')
def api_stats():
    """API для получения статистики пользователей"""
    stats = db.get_user_type_statistics()
    return jsonify(stats)

@users.route('/api/search')
def api_search():
    """API для поиска пользователей"""
    query = request.args.get('q')
    faculty = request.args.get('faculty')
    user_type = request.args.get('type')
    limit = int(request.args.get('limit', 20))
    
    users_data = db.search_users(
        query=query,
        faculty=faculty,
        user_type=user_type,
        limit=limit
    )
    
    return jsonify({
        'users': users_data,
        'count': len(users_data)
    }) 