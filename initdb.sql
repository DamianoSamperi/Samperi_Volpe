CREATE DATABASE IF NOT EXISTS controllertratte;

USE controllertratte;

CREATE TABLE IF NOT EXISTS tratte_salvate (
        id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        origine VARCHAR(3) NOT NULL,
        destinazione VARCHAR(3) NOT NULL,
        adulti INT
);
CREATE TABLE IF NOT EXISTS aeroporti_salvati (
        id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        origine VARCHAR(3) NOT NULL
);

CREATE DATABASE IF NOT EXISTS rules;

USE rules;

CREATE TABLE IF NOT EXISTS tratte (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        origine TEXT NOT NULL,
        destinazione TEXT NOT NULL,
        budget INTEGER,
        adulti INTEGER
);

CREATE TABLE IF NOT EXISTS aeroporti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        origine TEXT NOT NULL,
        budget INTEGER
);

CREATE DATABASE IF NOT EXISTS scraper;

USE scraper;

CREATE TABLE IF NOT EXISTS tratte_salvate (
        id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        origine VARCHAR(3) NOT NULL,
        destinazione VARCHAR(3) NOT NULL,
        adulti INT
);
CREATE TABLE IF NOT EXISTS aeroporti_salvati (
        id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        origine VARCHAR(3) NOT NULL
);

CREATE DATABASE IF NOT EXISTS metrics;

USE metrics;

CREATE TABLE IF NOT EXISTS metrica (
        id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        metrica VARCHAR(3) NOT NULL,
        soglia FLOAT UNSIGNED
);

CREATE DATABASE IF NOT EXISTS users;

USE users;

CREATE TABLE IF NOT EXISTS users (
        id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(20) NOT NULL,
        cognome VARCHAR(20) NOT NULL,
        email VARCHAR(20) NOT NULL
);
