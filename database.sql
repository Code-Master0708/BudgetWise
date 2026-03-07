USE budgetwise_db;

-- Drop the old table if it exists to avoid conflicts
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Optional: Insert a test user
INSERT INTO users (username, email, password) VALUES ('DemoUser', 'test@budgetwise.ai', 'password123');
