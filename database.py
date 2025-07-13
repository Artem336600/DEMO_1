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
    
    def _save_find_people_data(self, user_id, data):
        """Сохранение данных для поиска участников"""
        insert_data = {
            'user_id': user_id,
            'project_description': data.get('project_description'),
            'looking_for': data.get('looking_for')
        }
        
        result = self.supabase.table('find_people_data').insert(insert_data).execute()
        if not result.data:
            raise Exception("Ошибка при сохранении данных поиска участников")
    
    def _save_join_project_data(self, user_id, data):
        """Сохранение данных для участия в проектах"""
        insert_data = {
            'user_id': user_id,
            'what_to_do': data.get('what_to_do'),
            'interests': data.get('interests'),
            'time_commitment': data.get('time_commitment', [])
        }
        
        result = self.supabase.table('join_project_data').insert(insert_data).execute()
        if not result.data:
            raise Exception("Ошибка при сохранении данных участия в проектах")
    
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
        """Фильтрует пользователей по навыкам из дополнительных таблиц"""
        if not skills:
            return users
        
        filtered_users = []
        skills_lower = [skill.lower() for skill in skills]
        
        for user in users:
            user_id = user['id']
            purpose = user['purpose']
            
            # Проверяем навыки в зависимости от типа пользователя
            has_matching_skills = False
            
            try:
                if purpose == 'find_people':
                    # Ищем в looking_for
                    result = self.supabase.table('find_people_data').select('looking_for').eq('user_id', user_id).execute()
                    if result.data:
                        looking_for = result.data[0].get('looking_for', '')
                        if looking_for:
                            user_skills = [skill.strip().lower() for skill in looking_for.split(',')]
                            has_matching_skills = any(
                                any(search_skill in user_skill for search_skill in skills_lower)
                                for user_skill in user_skills
                            )
                
                elif purpose == 'join_project':
                    # Ищем в what_to_do и interests
                    result = self.supabase.table('join_project_data').select('what_to_do, interests').eq('user_id', user_id).execute()
                    if result.data:
                        data = result.data[0]
                        what_to_do = data.get('what_to_do', '')
                        interests = data.get('interests', '')
                        
                        all_skills = []
                        if what_to_do:
                            all_skills.extend([skill.strip().lower() for skill in what_to_do.split(',')])
                        if interests:
                            all_skills.extend([skill.strip().lower() for skill in interests.split(',')])
                        
                        has_matching_skills = any(
                            any(search_skill in user_skill for search_skill in skills_lower)
                            for user_skill in all_skills
                        )
                
                elif purpose == 'expand_network':
                    # Ищем в discuss_topics
                    result = self.supabase.table('expand_network_data').select('discuss_topics').eq('user_id', user_id).execute()
                    if result.data:
                        discuss_topics = result.data[0].get('discuss_topics', '')
                        if discuss_topics:
                            user_topics = [topic.strip().lower() for topic in discuss_topics.split(',')]
                            has_matching_skills = any(
                                any(search_skill in user_topic for search_skill in skills_lower)
                                for user_topic in user_topics
                            )
                
                # Также проверяем в описании about
                about = user.get('about', '')
                if about and not has_matching_skills:
                    about_lower = about.lower()
                    has_matching_skills = any(skill in about_lower for skill in skills_lower)
                
                if has_matching_skills:
                    filtered_users.append(user)
                    
            except Exception as e:
                print(f"Ошибка при фильтрации по навыкам для пользователя {user_id}: {str(e)}")
                continue
        
        return filtered_users

# Глобальный экземпляр для использования в приложении
db = DatabaseManager() 