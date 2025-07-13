import json
from mistralai import Mistral
from config import Config

class QueryParser:
    def __init__(self):
        self.mistral_client = Mistral(api_key=Config.MISTRAL_API_KEY)
    
    def parse_query_semantically(self, query):
        """Извлекает навыки, курс, тип пользователя, факультет и номер группы из смысла запроса с помощью Mistral AI."""
        
        # Маппинг факультетов
        faculty_mapping = {
            "информатика": "ИУ",
            "информационные технологии": "ИУ",
            "программирование": "ИУ",
            "бизнес": "ИБМ",
            "менеджмент": "ИБМ",
            "машиностроение": "МТ",
            "специальное машиностроение": "СМ",
            "биомедицина": "БМТ",
            "радиоэлектроника": "РЛ",
            "энергомашиностроение": "Э",
            "робототехника": "РК",
            "фундаментальные науки": "ФН",
            "лингвистика": "Л",
            "безопасность": "ЮР",
            "гуманитарные науки": "СГН"
        }
        
        prompt = f"""
        Проанализируй следующий запрос и извлеки из него навыки, курс, тип пользователя, факультет и номер группы, если они присутствуют.
        
        ВАЖНО: Также определи для каждого параметра, является ли он обязательным (required) или необязательным (optional) на основе контекста запроса.
        
        Параметр считается обязательным, если:
        - Он явно указан в запросе с конкретным значением
        - Используются слова типа "нужен", "обязательно", "только", "именно"
        - Контекст подразумевает строгое требование
        
        Параметр считается необязательным, если:
        - Он упоминается как предпочтение ("желательно", "предпочтительно", "лучше")
        - Используются слова типа "можно", "возможно", "по возможности"
        - Контекст подразумевает гибкость
        
        - Навыки — это умения или области знаний. Если указаны конкретные технологии (например, Python, Java), извлеки их. Если указана общая категория (например, программирование, дизайн, анализ данных), извлеки её. Если навыки не указаны, верни [].
        - Курс — это уровень обучения (например, 1, 2, 3, 4, 5, 6, магистратура, аспирантура).
        - Тип пользователя — это цель или роль пользователя, одна из следующих категорий: 
          "Поиск участников для проекта", "Участие в существующих проектах", "Расширение профессиональных контактов". Если категория не соответствует, укажи null.
        - Факультет — это название факультета или направления (например, физический, информационные технологии).
        - Номер группы — это идентификатор учебной группы (например, ИТ-301, Ф-21, М-1).
        
        Если какая-то информация отсутствует, укажи null (для навыков — []).
        
        Ответь в формате JSON:
        {{
            "навыки": [],
            "курс": null,
            "тип пользователя": null,
            "факультет": null,
            "номер группы": null,
            "requirements": {{
                "навыки": "required|optional|null",
                "курс": "required|optional|null",
                "тип пользователя": "required|optional|null",
                "факультет": "required|optional|null",
                "номер группы": "required|optional|null"
            }}
        }}
        
        Запрос: {query}
        """

        try:
            response = self.mistral_client.chat.complete(
                model="mistral-medium",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )

            if response and response.choices:
                parsed_data = json.loads(response.choices[0].message.content)
                
                # Преобразуем факультеты в коды
                faculty_raw = parsed_data.get("факультет")
                if faculty_raw:
                    faculty_lower = faculty_raw.lower()
                    for key, value in faculty_mapping.items():
                        if key in faculty_lower:
                            parsed_data["faculty_code"] = value
                            break
                    else:
                        parsed_data["faculty_code"] = None
                else:
                    parsed_data["faculty_code"] = None
                
                return {
                    "skills": parsed_data.get("навыки", []),
                    "course": parsed_data.get("курс"),
                    "user_type": parsed_data.get("тип пользователя"),
                    "faculty": parsed_data.get("факультет"),
                    "faculty_code": parsed_data.get("faculty_code"),
                    "group": parsed_data.get("номер группы"),
                    "requirements": parsed_data.get("requirements", {}),
                    "raw_response": parsed_data
                }
            else:
                return self._empty_response()
                
        except Exception as e:
            print(f"Ошибка при разборе запроса: {e}")
            return self._empty_response()
    
    def _empty_response(self):
        """Возвращает пустой ответ при ошибке"""
        return {
            "skills": [],
            "course": None,
            "user_type": None,
            "faculty": None,
            "faculty_code": None,
            "group": None,
            "requirements": {},
            "raw_response": {}
        }
    
    def build_search_filters(self, parsed_query):
        """Создает фильтры для поиска на основе разобранного запроса"""
        filters = {}
        
        if parsed_query["course"]:
            if isinstance(parsed_query["course"], int):
                filters["course"] = f"{parsed_query['course']} курс"
            else:
                filters["course"] = parsed_query["course"]
        
        # Маппинг типов пользователей для фильтров
        user_type_mapping = {
            "Поиск участников для проекта": "project_creator",
            "Участие в существующих проектах": "project_participant", 
            "Расширение профессиональных контактов": "networker"
        }
        
        if parsed_query["user_type"] and parsed_query["user_type"] in user_type_mapping:
            filters["user_type"] = user_type_mapping[parsed_query["user_type"]]
        
        if parsed_query["faculty_code"]:
            filters["faculty"] = parsed_query["faculty_code"]
        
        if parsed_query["group"]:
            filters["group_name"] = parsed_query["group"]
        
        return filters

# Глобальный экземпляр
query_parser = QueryParser() 