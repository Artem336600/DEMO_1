-- Создание enum для типов пользователей
DROP TYPE IF EXISTS user_type_enum CASCADE;
CREATE TYPE user_type_enum AS ENUM (
    'project_creator',    -- Поиск участников для проекта
    'project_participant', -- Участие в существующих проектах
    'networker',          -- Расширение профессиональных контактов
    'explorer'            -- Изучение возможностей платформы
);

-- Создание таблицы пользователей
CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    faculty VARCHAR(50) NOT NULL,
    course VARCHAR(50) NOT NULL,
    group_name VARCHAR(50) NOT NULL,
    telegram VARCHAR(100) NOT NULL,
    github VARCHAR(255),
    portfolio VARCHAR(255),
    photo_url VARCHAR(255),
    purpose VARCHAR(50) NOT NULL,
    user_type user_type_enum NOT NULL,
    about TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание таблицы для данных "поиск участников"
CREATE TABLE find_people_data (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    project_description TEXT,
    looking_for TEXT, -- comma-separated tags
    required_skills TEXT, -- comma-separated skills
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание таблицы для данных "участие в проектах"
CREATE TABLE join_project_data (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    what_to_do TEXT, -- comma-separated tags
    interests TEXT, -- comma-separated tags
    my_skills TEXT, -- comma-separated skills
    time_commitment TEXT[], -- array of time commitments
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание таблицы для данных "расширение сети"
CREATE TABLE expand_network_data (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    meet_with TEXT[], -- array of preferences
    communication_format TEXT[], -- array of formats
    discuss_topics TEXT, -- comma-separated tags
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание индексов для быстрого поиска
CREATE INDEX idx_users_faculty ON users(faculty);
CREATE INDEX idx_users_course ON users(course);
CREATE INDEX idx_users_purpose ON users(purpose);
CREATE INDEX idx_users_user_type ON users(user_type);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Включение Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE find_people_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE join_project_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE expand_network_data ENABLE ROW LEVEL SECURITY;

-- Создание политик безопасности (базовые - можно настроить позже)
CREATE POLICY "Users can view all profiles" ON users FOR SELECT USING (true);
CREATE POLICY "Users can insert their own profile" ON users FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can update their own profile" ON users FOR UPDATE USING (true);

CREATE POLICY "Users can view all find_people_data" ON find_people_data FOR SELECT USING (true);
CREATE POLICY "Users can insert their own find_people_data" ON find_people_data FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can view all join_project_data" ON join_project_data FOR SELECT USING (true);
CREATE POLICY "Users can insert their own join_project_data" ON join_project_data FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can view all expand_network_data" ON expand_network_data FOR SELECT USING (true);
CREATE POLICY "Users can insert their own expand_network_data" ON expand_network_data FOR INSERT WITH CHECK (true);

-- Создание функции для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Создание триггера для автоматического обновления updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Таблицы для отслеживания свободного ввода пользователей
-- Таблица для отслеживания навыков/компетенций
CREATE TABLE user_skills_input (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    skill_name VARCHAR(255) NOT NULL,
    input_context VARCHAR(50) NOT NULL, -- 'looking_for', 'what_to_do', 'interests', 'required_skills', 'my_skills'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Таблица для отслеживания тем для обсуждения
CREATE TABLE user_topics_input (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    topic_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Таблица для отслеживания описаний проектов
CREATE TABLE project_descriptions_input (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Таблица для отслеживания описаний "о себе"
CREATE TABLE about_descriptions_input (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы для аналитики
CREATE INDEX idx_user_skills_input_skill_name ON user_skills_input(skill_name);
CREATE INDEX idx_user_skills_input_context ON user_skills_input(input_context);
CREATE INDEX idx_user_skills_input_created_at ON user_skills_input(created_at);
CREATE INDEX idx_user_topics_input_topic_name ON user_topics_input(topic_name);
CREATE INDEX idx_user_topics_input_created_at ON user_topics_input(created_at);
CREATE INDEX idx_project_descriptions_input_created_at ON project_descriptions_input(created_at);
CREATE INDEX idx_about_descriptions_input_created_at ON about_descriptions_input(created_at);

-- RLS для новых таблиц
ALTER TABLE user_skills_input ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_topics_input ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_descriptions_input ENABLE ROW LEVEL SECURITY;
ALTER TABLE about_descriptions_input ENABLE ROW LEVEL SECURITY;

-- Политики безопасности для новых таблиц
CREATE POLICY "Admin can view all skills input" ON user_skills_input FOR SELECT USING (true);
CREATE POLICY "Users can insert their own skills input" ON user_skills_input FOR INSERT WITH CHECK (true);

CREATE POLICY "Admin can view all topics input" ON user_topics_input FOR SELECT USING (true);
CREATE POLICY "Users can insert their own topics input" ON user_topics_input FOR INSERT WITH CHECK (true);

CREATE POLICY "Admin can view all project descriptions input" ON project_descriptions_input FOR SELECT USING (true);
CREATE POLICY "Users can insert their own project descriptions input" ON project_descriptions_input FOR INSERT WITH CHECK (true);

CREATE POLICY "Admin can view all about descriptions input" ON about_descriptions_input FOR SELECT USING (true);
CREATE POLICY "Users can insert their own about descriptions input" ON about_descriptions_input FOR INSERT WITH CHECK (true); 