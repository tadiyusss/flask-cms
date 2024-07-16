CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(128) NOT NULL UNIQUE,
    firstname VARCHAR(128) NOT NULL,
    lastname VARCHAR(128) NOT NULL,
    password VARCHAR(254) NOT NULL,
    salt VARCHAR(254) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    login_id VARCHAR(64) NOT NULL,
    avatar_file VARCHAR(128) DEFAULT 'profile.svg',
    user_type VARCHAR(64) NOT NULL
);

CREATE TABLE IF NOT EXISTS extensions (
    blueprint VARCHAR(64) NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT 1,
    name VARCHAR(64) NOT NULL,
    version VARCHAR(6) NOT NULL,
    description TEXT,
    url_prefix VARCHAR(255) DEFAULT '/',
    template_folder VARCHAR(64) DEFAULT 'templates',
    static_folder VARCHAR(20) NOT NULL DEFAULT 'static',
    static_url_path VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS navigation (
    blueprint VARCHAR(64) NOT NULL,
    navigation_name VARCHAR(24) NOT NULL,
    redirect_to VARCHAR(124) NOT NULL
);



