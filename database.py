from supabase import create_client, Client
from config import Config
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    def _get_user_type_from_purpose(self, purpose):
        """Определение типа пользователя на основе цели регистрации"""
        purpose_to_type = {
            'find_people': 'project_creator',
            'join_project': 'project_participant', 
            'expand_network': 'networker',
            'explore': 'explorer'
        }
        return purpose_to_type.get(purpose, 'explorer')
    
    def _save_find_people_data(self, user_id, data):
        """Сохранение данных для поиска участников"""
        insert_data = {
            'user_id': user_id,
            'project_description': data.get('project_description'),
            'looking_for': data.get('looking_for'),
            'required_skills': data.get('required_skills')
        }
        
        result = self.supabase.table('find_people_data').insert(insert_data).execute()
        if not result.data:
            raise Exception("Ошибка при сохранении данных поиска участников")
        
        # Сохранение данных для аналитики
        self._save_project_description_input(user_id, data.get('project_description'))
        self._save_skills_input(user_id, data.get('looking_for'), 'looking_for')
        self._save_skills_input(user_id, data.get('required_skills'), 'required_skills')
    
    def _save_join_project_data(self, user_id, data):
        """Сохранение данных для участия в проектах"""
        insert_data = {
            'user_id': user_id,
            'what_to_do': data.get('what_to_do'),
            'interests': data.get('interests'),
            'my_skills': data.get('my_skills'),
            'time_commitment': data.get('time_commitment', [])
        }
        
        result = self.supabase.table('join_project_data').insert(insert_data).execute()
        if not result.data:
            raise Exception("Ошибка при сохранении данных участия в проектах")
        
        # Сохранение данных для аналитики
        self._save_skills_input(user_id, data.get('what_to_do'), 'what_to_do')
        self._save_skills_input(user_id, data.get('interests'), 'interests')
        self._save_skills_input(user_id, data.get('my_skills'), 'my_skills')
    
    def _save_expand_network_data(self, user_id, data):
        """Сохранение данных для расширения сети"""
        insert_data = {
            'user_id': user_id,
            'meet_with': data.get('meet_with', []),
            'communication_format': data.get('communication_format', []),
            'discuss_topics': data.get('discuss_topics')
        }
        
        result = self.supabase.table('expand_network_data').insert(insert_data).execute()
        if not result.data:
            raise Exception("Ошибка при сохранении данных расширения сети")
        
        # Сохранение данных для аналитики
        self._save_topics_input(user_id, data.get('discuss_topics'))
    
    def _save_skills_input(self, user_id, skills_string, context):
        """Сохранение навыков/компетенций в таблицу аналитики"""
        if not skills_string:
            return
            
        skills = [skill.strip() for skill in skills_string.split(',') if skill.strip()]
        
        for skill in skills:
            try:
                insert_data = {
                    'user_id': user_id,
                    'skill_name': skill,
                    'input_context': context
                }
                self.supabase.table('user_skills_input').insert(insert_data).execute()
            except Exception as e:
                print(f"Ошибка при сохранении навыка '{skill}': {str(e)}")
    
    def _save_topics_input(self, user_id, topics_string):
        """Сохранение тем для обсуждения в таблицу аналитики"""
        if not topics_string:
            return
            
        topics = [topic.strip() for topic in topics_string.split(',') if topic.strip()]
        
        for topic in topics:
            try:
                insert_data = {
                    'user_id': user_id,
                    'topic_name': topic
                }
                self.supabase.table('user_topics_input').insert(insert_data).execute()
            except Exception as e:
                print(f"Ошибка при сохранении темы '{topic}': {str(e)}")
    
    def _save_project_description_input(self, user_id, description):
        """Сохранение описания проекта в таблицу аналитики"""
        if not description:
            return
            
        try:
            insert_data = {
                'user_id': user_id,
                'description': description
            }
            self.supabase.table('project_descriptions_input').insert(insert_data).execute()
        except Exception as e:
            print(f"Ошибка при сохранении описания проекта: {str(e)}")
    
    def _save_about_description_input(self, user_id, description):
        """Сохранение описания 'о себе' в таблицу аналитики"""
        if not description:
            return
            
        try:
            insert_data = {
                'user_id': user_id,
                'description': description
            }
            self.supabase.table('about_descriptions_input').insert(insert_data).execute()
        except Exception as e:
            print(f"Ошибка при сохранении описания 'о себе': {str(e)}")
    
    def save_user_registration(self, user_data, step3_data=None, about=None):
        """Сохранение полной регистрации пользователя"""
        try:
            # Определение типа пользователя
            user_type = self._get_user_type_from_purpose(user_data['purpose'])
            
            # Сохранение основных данных пользователя
            user_insert_data = {
                'full_name': user_data['full_name'],
                'faculty': user_data['faculty'],
                'course': user_data['course'],
                'group_name': user_data['group'],
                'telegram': user_data['telegram'],
                'github': user_data.get('github'),
                'portfolio': user_data.get('portfolio'),
                'photo_url': user_data.get('photo'),
                'purpose': user_data['purpose'],
                'user_type': user_type,
                'about': about
            }
            
            # Вставка пользователя
            user_result = self.supabase.table('users').insert(user_insert_data).execute()
            
            if not user_result.data:
                raise Exception("Ошибка при создании пользователя")
            
            user_id = user_result.data[0]['id']
            
            # Сохранение описания "о себе" для аналитики
            self._save_about_description_input(user_id, about)
            
            # Сохранение дополнительных данных в зависимости от цели
            if step3_data:
                purpose = user_data['purpose']
                
                if purpose == 'find_people':
                    self._save_find_people_data(user_id, step3_data)
                elif purpose == 'join_project':
                    self._save_join_project_data(user_id, step3_data)
                elif purpose == 'expand_network':
                    self._save_expand_network_data(user_id, step3_data)
            
            return user_id
            
        except Exception as e:
            print(f"Ошибка при сохранении регистрации: {str(e)}")
            raise e
    
    def get_user_by_id(self, user_id):
        """Получение пользователя по ID"""
        try:
            result = self.supabase.table('users').select('*').eq('id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Ошибка при получении пользователя: {str(e)}")
            return None
    
    def search_users(self, query=None, faculty=None, purpose=None, user_type=None, limit=20):
        """Поиск пользователей с фильтрами"""
        try:
            query_builder = self.supabase.table('users').select('*')
            
            if faculty:
                query_builder = query_builder.eq('faculty', faculty)
            
            if purpose:
                query_builder = query_builder.eq('purpose', purpose)
            
            if user_type:
                query_builder = query_builder.eq('user_type', user_type)
            
            if query:
                query_builder = query_builder.ilike('full_name', f'%{query}%')
            
            result = query_builder.limit(limit).execute()
            return result.data
            
        except Exception as e:
            print(f"Ошибка при поиске пользователей: {str(e)}")
            return []
    
    def get_users_by_type(self, user_type, limit=20):
        """Получение пользователей по типу"""
        try:
            result = self.supabase.table('users').select('*').eq('user_type', user_type).limit(limit).execute()
            return result.data
        except Exception as e:
            print(f"Ошибка при получении пользователей по типу: {str(e)}")
            return []
    
    def get_user_type_statistics(self):
        """Получение статистики по типам пользователей"""
        try:
            result = self.supabase.table('users').select('user_type').execute()
            
            stats = {
                'project_creator': 0,
                'project_participant': 0,
                'networker': 0,
                'explorer': 0
            }
            
            for user in result.data:
                user_type = user.get('user_type')
                if user_type in stats:
                    stats[user_type] += 1
            
            return stats
        except Exception as e:
            print(f"Ошибка при получении статистики: {str(e)}")
            return {}
    
    def get_user_type_description(self, user_type):
        """Получение описания типа пользователя"""
        descriptions = {
            'project_creator': 'Создатель проектов - ищет участников для своих проектов',
            'project_participant': 'Участник проектов - хочет присоединиться к существующим проектам',
            'networker': 'Нетворкер - расширяет профессиональные контакты',
            'explorer': 'Исследователь - изучает возможности платформы'
        }
        return descriptions.get(user_type, 'Неизвестный тип')
    
    def get_users_with_purpose_data(self, purpose, limit=20):
        """Получение пользователей с их дополнительными данными по цели"""
        try:
            if purpose == 'find_people':
                result = self.supabase.table('users').select('''
                    *, find_people_data(*)
                ''').eq('purpose', purpose).limit(limit).execute()
            elif purpose == 'join_project':
                result = self.supabase.table('users').select('''
                    *, join_project_data(*)
                ''').eq('purpose', purpose).limit(limit).execute()
            elif purpose == 'expand_network':
                result = self.supabase.table('users').select('''
                    *, expand_network_data(*)
                ''').eq('purpose', purpose).limit(limit).execute()
            else:
                result = self.supabase.table('users').select('*').eq('purpose', purpose).limit(limit).execute()
            
            return result.data
            
        except Exception as e:
            print(f"Ошибка при получении пользователей с данными цели: {str(e)}")
            return []

    def advanced_search(self, query=None, filters=None, skills=None, limit=20):
        """Расширенный поиск пользователей с фильтрами и поиском по навыкам"""
        try:
            query_builder = self.supabase.table('users').select('*')
            
            # Применяем фильтры
            if filters:
                if filters.get('faculty'):
                    query_builder = query_builder.eq('faculty', filters['faculty'])
                
                if filters.get('course'):
                    query_builder = query_builder.eq('course', filters['course'])
                
                if filters.get('user_type'):
                    query_builder = query_builder.eq('user_type', filters['user_type'])
                
                if filters.get('group_name'):
                    query_builder = query_builder.eq('group_name', filters['group_name'])
            
            # Поиск по имени
            if query:
                query_builder = query_builder.ilike('full_name', f'%{query}%')
            
            result = query_builder.limit(limit).execute()
            users = result.data
            
            # Если есть навыки для поиска, фильтруем по ним
            if skills and users:
                users = self._filter_by_skills(users, skills)
            
            return users
            
        except Exception as e:
            print(f"Ошибка при расширенном поиске: {str(e)}")
            return []
    
    def _filter_by_skills(self, users, skills):
        """Фильтрация пользователей по навыкам"""
        if not skills:
            return users
        
        filtered_users = []
        for user in users:
            user_skills = []
            
            # Получение навыков из разных источников в зависимости от типа пользователя
            if user.get('purpose') == 'find_people':
                # Для создателей проектов ищем в looking_for и required_skills
                find_data = self.supabase.table('find_people_data').select('looking_for, required_skills').eq('user_id', user['id']).execute()
                if find_data.data:
                    user_skills.extend(find_data.data[0].get('looking_for', '').split(','))
                    user_skills.extend(find_data.data[0].get('required_skills', '').split(','))
                    
            elif user.get('purpose') == 'join_project':
                # Для участников проектов ищем в what_to_do, interests и my_skills
                join_data = self.supabase.table('join_project_data').select('what_to_do, interests, my_skills').eq('user_id', user['id']).execute()
                if join_data.data:
                    user_skills.extend(join_data.data[0].get('what_to_do', '').split(','))
                    user_skills.extend(join_data.data[0].get('interests', '').split(','))
                    user_skills.extend(join_data.data[0].get('my_skills', '').split(','))
            
            # Очистка и нормализация навыков
            user_skills = [skill.strip().lower() for skill in user_skills if skill.strip()]
            skills_lower = [skill.lower() for skill in skills]
            
            # Проверка пересечения навыков
            if any(skill in user_skills for skill in skills_lower):
                filtered_users.append(user)
        
        return filtered_users
    
    # Методы для получения аналитики пользовательского ввода
    def get_popular_skills(self, context=None, limit=50):
        """Получение популярных навыков/компетенций"""
        try:
            query = self.supabase.table('user_skills_input').select('skill_name, input_context')
            
            if context:
                query = query.eq('input_context', context)
            
            result = query.execute()
            
            if not result.data:
                return []
            
            # Подсчет популярности
            skill_counts = {}
            for record in result.data:
                skill = record['skill_name'].lower().strip()
                if skill:
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1
            
            # Сортировка по популярности
            popular_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
            return popular_skills[:limit]
            
        except Exception as e:
            print(f"Ошибка при получении популярных навыков: {str(e)}")
            return []
    
    def get_popular_topics(self, limit=30):
        """Получение популярных тем для обсуждения"""
        try:
            result = self.supabase.table('user_topics_input').select('topic_name').execute()
            
            if not result.data:
                return []
            
            # Подсчет популярности
            topic_counts = {}
            for record in result.data:
                topic = record['topic_name'].lower().strip()
                if topic:
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            # Сортировка по популярности
            popular_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
            return popular_topics[:limit]
            
        except Exception as e:
            print(f"Ошибка при получении популярных тем: {str(e)}")
            return []
    
    def get_skills_by_context(self, context, limit=30):
        """Получение навыков по контексту (looking_for, what_to_do, interests, required_skills, my_skills)"""
        try:
            result = self.supabase.table('user_skills_input').select('skill_name').eq('input_context', context).execute()
            
            if not result.data:
                return []
            
            # Подсчет популярности
            skill_counts = {}
            for record in result.data:
                skill = record['skill_name'].lower().strip()
                if skill:
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1
            
            # Сортировка по популярности
            popular_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
            return popular_skills[:limit]
            
        except Exception as e:
            print(f"Ошибка при получении навыков по контексту: {str(e)}")
            return []
    
    def get_project_descriptions_analysis(self, limit=100):
        """Получение описаний проектов для анализа"""
        try:
            result = self.supabase.table('project_descriptions_input').select('description, created_at').order('created_at', desc=True).limit(limit).execute()
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Ошибка при получении описаний проектов: {str(e)}")
            return []
    
    def get_about_descriptions_analysis(self, limit=100):
        """Получение описаний 'о себе' для анализа"""
        try:
            result = self.supabase.table('about_descriptions_input').select('description, created_at').order('created_at', desc=True).limit(limit).execute()
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Ошибка при получении описаний 'о себе': {str(e)}")
            return []
    
    def get_user_input_statistics(self):
        """Получение статистики пользовательского ввода"""
        try:
            stats = {}
            
            # Статистика навыков
            skills_result = self.supabase.table('user_skills_input').select('input_context').execute()
            if skills_result.data:
                context_counts = {}
                for record in skills_result.data:
                    context = record['input_context']
                    context_counts[context] = context_counts.get(context, 0) + 1
                stats['skills_by_context'] = context_counts
                stats['total_skills'] = len(skills_result.data)
            
            # Статистика тем
            topics_result = self.supabase.table('user_topics_input').select('*').execute()
            if topics_result.data:
                stats['total_topics'] = len(topics_result.data)
            
            # Статистика описаний проектов
            projects_result = self.supabase.table('project_descriptions_input').select('*').execute()
            if projects_result.data:
                stats['total_project_descriptions'] = len(projects_result.data)
            
            # Статистика описаний "о себе"
            about_result = self.supabase.table('about_descriptions_input').select('*').execute()
            if about_result.data:
                stats['total_about_descriptions'] = len(about_result.data)
            
            return stats
            
        except Exception as e:
            print(f"Ошибка при получении статистики: {str(e)}")
            return {}

# Глобальный экземпляр для использования в приложении
db = DatabaseManager() 