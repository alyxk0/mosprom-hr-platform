-- Создаём таблицу пользователей
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),  -- Уникальный идентификатор
    email TEXT UNIQUE NOT NULL,                     -- Почта (уникальная)
    password_hash TEXT NOT NULL,                    -- Захэшированный пароль (через werkzeug.generate_password_hash)
    user_type TEXT NOT NULL CHECK (user_type IN ('student', 'organization', 'university')), -- тип пользователя
    created_at TIMESTAMP DEFAULT NOW(),             -- дата создания
    updated_at TIMESTAMP DEFAULT NOW()              -- дата последнего обновления
);

-- Обновляем updated_at автоматически при изменениях
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_timestamp
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Убедись, что расширение есть (для gen_random_uuid)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Таблица резюме
CREATE TABLE IF NOT EXISTS resumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    data JSONB NOT NULL,               -- само резюме в формате JSON
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Триггер обновления updated_at
CREATE OR REPLACE FUNCTION resumes_update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_resumes_update_timestamp
BEFORE UPDATE ON resumes
FOR EACH ROW
EXECUTE FUNCTION resumes_update_timestamp();
