
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    status ENUM('active', 'blocked') NOT NULL
);

CREATE TABLE logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resource_name VARCHAR(255) NOT NULL,
    category VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    level ENUM('Low', 'Med', 'High', 'Info', 'Error') NOT NULL
);
