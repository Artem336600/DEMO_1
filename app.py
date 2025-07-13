import os
from flask import Flask, render_template, request, jsonify
from routes.auth import auth
from routes.users import users
from config import Config
from services.query_parser import query_parser
from database import db

app = Flask(__name__)
app.config.from_object(Config)

# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(users)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        data = request.get_json()
        query = data.get('query', '')
        tags = data.get('tags', {})
        required_fields = data.get('required_fields', [])
    else:
        query = request.args.get('q', '')
        tags = {}
        required_fields = []
    
    print(f"[DEBUG] Поисковый запрос: '{query}'")
    print(f"[DEBUG] Теги: {tags}")
    print(f"[DEBUG] Обязательные поля: {required_fields}")
    
    if not query:
        return jsonify({'results': [], 'query': query, 'parsed': {}})
    
    try:
        # Семантический разбор запроса
        print(f"[DEBUG] Начинаем семантический разбор...")
        parsed_query = query_parser.parse_query_semantically(query)
        print(f"[DEBUG] Результат разбора: {parsed_query}")
        
        # Объединяем результаты разбора с тегами
        final_query = parsed_query.copy()
        
        # Добавляем теги к соответствующим полям
        for tag_type, tag_values in tags.items():
            if tag_type in final_query:
                if isinstance(final_query[tag_type], list):
                    final_query[tag_type].extend(tag_values)
                else:
                    final_query[tag_type] = tag_values
            else:
                final_query[tag_type] = tag_values
        
        # Возвращаем только результат разбора, без поиска в базе
        response_data = {
            'query': query,
            'parsed': final_query,
            'required_fields': required_fields,
            'message': 'Запрос успешно разобран'
        }
        print(f"[DEBUG] Отправляем результат разбора")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"[ERROR] Ошибка при разборе запроса: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'query': query,
            'error': str(e),
            'parsed': {}
        })

if __name__ == '__main__':
    app.run(debug=True) 