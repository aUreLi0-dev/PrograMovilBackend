-- migrate:up

CREATE TABLE app_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(30) NOT NULL UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    institutional_email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    google_id VARCHAR(255),
    token_version INTEGER NOT NULL DEFAULT 1
);

-- migrate:down

DROP TABLE IF EXISTS app_user;
