CREATE TABLE IF NOT EXISTS Movies(
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    year INT,
    director VARCHAR(255),
    genre VARCHAR(255),
    country VARCHAR(255)
)