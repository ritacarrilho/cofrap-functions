CREATE DATABASE IF NOT EXISTS cofrap_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
  
USE cofrap_db;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100) NOT NULL,
  password TEXT NOT NULL,
  mfa TEXT NOT NULL,
  gendate BIGINT NOT NULL,
  expired TINYINT(1) DEFAULT 0
);

INSERT INTO users (username, password, mfa, gendate, expired) VALUES
  (
    'michel.ranu',
    'QUFBQS4uLkdHR0c9PQ==',     -- "AAAA...GGGG=="
    'QUFBQS4uLkJCQkI9',         -- "AAAA...BBBB="
    1721916574,
    0
  ),
  (
    'sophie.duron',
    'U09QSElFLjEyMzQ1Ng==',     -- "SOPHIE.123456"
    'TURTUkEy',                 -- "MDRMA2"
    1721918888,
    0
  ),
  (
    'alex.martin',
    'YWxleC5tYXJ0aW4xMjM=',     -- "alex.martin123"
    'bWZhX2tleTEyMw==',         -- "mfa_key123"
    1721920000,
    1
  );
