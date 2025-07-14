-- Миграция для добавления полей навыков
-- Добавляем поле required_skills в таблицу find_people_data
ALTER TABLE find_people_data ADD COLUMN IF NOT EXISTS required_skills TEXT;

-- Добавляем поле my_skills в таблицу join_project_data  
ALTER TABLE join_project_data ADD COLUMN IF NOT EXISTS my_skills TEXT;

-- Обновляем комментарий для таблицы user_skills_input (информационно)
COMMENT ON COLUMN user_skills_input.input_context IS 'Контекст ввода навыка: looking_for, what_to_do, interests, required_skills, my_skills';
