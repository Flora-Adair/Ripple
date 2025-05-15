-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    username TEXT UNIQUE,         -- optional username for login
    email TEXT UNIQUE,            -- optional email, especially for Google OAuth dorm parents
    password TEXT,                -- nullable if OAuth user
    dorm TEXT,                   -- optional dorm assignment
    is_dorm_parent BOOLEAN NOT NULL DEFAULT 0
);

-- Moods table
CREATE TABLE moods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    mood_score INTEGER NOT NULL CHECK(mood_score BETWEEN 1 AND 10),
    mood_description TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
