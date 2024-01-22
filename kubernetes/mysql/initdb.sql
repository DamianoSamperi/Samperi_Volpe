CREATE DATABASE IF NOT EXISTS controllertratte;

USE controllertratte;

CREATE TABLE IF NOT EXISTS tratte_salvate (
        id INT PRIMARY KEY AUTO_INCREMENT,
        origine VARCHAR(3) NOT NULL,
        destinazione VARCHAR(3) NOT NULL,
        adulti INT
);
CREATE TABLE IF NOT EXISTS aeroporti_salvati (
        id INT PRIMARY KEY AUTO_INCREMENT,
        origine VARCHAR(3) NOT NULL
);

CREATE DATABASE IF NOT EXISTS rules;

USE rules;

CREATE TABLE IF NOT EXISTS tratte (
        id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT NOT NULL,
        origine TEXT NOT NULL,
        destinazione TEXT NOT NULL,
        budget INT,
        adulti INT
);

CREATE TABLE IF NOT EXISTS aeroporti (
        id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT NOT NULL,
        origine TEXT NOT NULL,
        budget INT
);

CREATE DATABASE IF NOT EXISTS scraper;

USE scraper;

CREATE TABLE IF NOT EXISTS tratte_salvate (
        id INT PRIMARY KEY AUTO_INCREMENT,
        origine VARCHAR(3) NOT NULL,
        destinazione VARCHAR(3) NOT NULL,
        adulti INT
);
CREATE TABLE IF NOT EXISTS aeroporti_salvati (
        id INT PRIMARY KEY AUTO_INCREMENT,
        origine VARCHAR(3) NOT NULL
);

CREATE DATABASE IF NOT EXISTS metrics;

USE metrics;

CREATE TABLE IF NOT EXISTS metrica (
        id INT PRIMARY KEY AUTO_INCREMENT,
        metrica VARCHAR(3) NOT NULL,
        soglia FLOAT UNSIGNED
);

CREATE DATABASE IF NOT EXISTS users;

USE users;

CREATE TABLE IF NOT EXISTS users (
        id INT PRIMARY KEY AUTO_INCREMENT,
        nome VARCHAR(20) NOT NULL,
        cognome VARCHAR(20) NOT NULL,
        email VARCHAR(50) NOT NULL
);
