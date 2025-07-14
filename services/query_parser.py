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
        
        ВАЖНО: Для каждого навыка определи отдельно:
        1. Является ли он обязательным (required) или необязательным (optional)
        2. Для необязательных навыков присвой баллы важности с учетом общего количества необязательных критериев:
           
           ПРАВИЛА РАСПРЕДЕЛЕНИЯ БАЛЛОВ:
           - Если 1 необязательный критерий: присвой 1 балл
           - Если 2 необязательных критерия: первый по важности 2 балла, второй 1 балл
           - Если 3 необязательных критерия: первый 3 балла, второй 2 балла, третий 1 балл
           - Если 4 необязательных критерия: первый 4 балла, второй 3 балла, третий 2 балла, четвертый 1 балл
           - Если 5+ необязательных критериев: первый 5 баллов, второй 4 балла, третий 3 балла, четвертый 2 балла, остальные по 1 баллу
           
           Баллы присваиваются на основе:
           - Порядка упоминания в тексте (первые обычно важнее)
           - Акцентов в тексте ("очень желательно" > "желательно")
           - Специфичности навыка (более общие навыки обычно важнее)
           - Связи с основной деятельностью
        
        Навык считается обязательным, если:
        - Он явно указан с словами "нужен", "обязательно", "только", "именно"
        - Контекст подразумевает строгое требование
        
        Навык считается необязательным, если:
        - Он упоминается как предпочтение ("желательно", "предпочтительно", "лучше")
        - Используются слова типа "можно", "возможно", "по возможности"
        - Контекст подразумевает гибкость
        
        - Навыки — это умения или области знаний. Если указаны конкретные технологии (например, Python, Java), извлеки их. Если указана общая категория (например, программирование, дизайн, анализ данных), извлеки её. Каждый навык должен быть объектом с полями "навык", "статус" и "баллы" (только для optional).
        - Курс — это уровень обучения (например, 1, 2, 3, 4, 5, 6, магистратура, аспирантура).
        - Тип пользователя — это цель или роль пользователя, одна из следующих категорий: 
          "Поиск участников для проекта", "Участие в существующих проектах", "Расширение профессиональных контактов". Если категория не соответствует, укажи null.
        - Факультет — это название факультета или направления (например, физический, информационные технологии).
        - Номер группы — это идентификатор учебной группы (например, ИТ-301, Ф-21, М-1).
        
        Если какая-то информация отсутствует, укажи null (для навыков — []).
        
        Ответь в формате JSON:
        {{
            "навыки": [
                {{"навык": "название навыка", "статус": "required|optional", "баллы": число_от_1_до_5_только_для_optional}}
            ],
            "курс": null,
            "тип пользователя": null,
            "факультет": null,
            "номер группы": null,
            "requirements": {{
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
                
                # Преобразуем навыки в старый формат для совместимости + добавляем новый формат
                skills_data = parsed_data.get("навыки", [])
                skills_list = []
                skills_with_status = []
                
                for skill_obj in skills_data:
                    if isinstance(skill_obj, dict) and "навык" in skill_obj:
                        skills_list.append(skill_obj["навык"])
                        # Добавляем поддержку баллов
                        skill_with_status = {
                            "навык": skill_obj["навык"],
                            "статус": skill_obj.get("статус", "optional")
                        }
                        # Добавляем баллы только для необязательных навыков
                        if skill_obj.get("статус") == "optional" and "баллы" in skill_obj:
                            skill_with_status["баллы"] = skill_obj["баллы"]
                        skills_with_status.append(skill_with_status)
                    else:
                        # Fallback для случаев, когда AI вернет просто строку
                        skills_list.append(str(skill_obj))
                        skills_with_status.append({
                            "навык": str(skill_obj), 
                            "статус": "optional",
                            "баллы": 3  # Средний балл по умолчанию
                        })
                
                return {
                    "skills": skills_list,  # Старый формат для совместимости
                    "skills_with_status": skills_with_status,  # Новый формат с статусами
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
            "skills_with_status": [],
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