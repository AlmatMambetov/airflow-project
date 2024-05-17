CREATE TABLE IF NOT EXISTS stage.currency_rub(
    id VARCHAR(255) NOT NULL,
    NumCode VARCHAR(255) NOT NULL,
    CharCode VARCHAR(255),
    Nominal int,
    Name VARCHAR(255),
    Value float,
    Previous float,
    date date NOT NULL
);