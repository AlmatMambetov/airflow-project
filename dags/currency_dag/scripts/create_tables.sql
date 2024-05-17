CREATE TABLE IF NOT EXISTS stage.currency_pound(
    title VARCHAR(255) NOT NULL,
    rate float,
    date date NOT NULL
);

CREATE TABLE IF NOT EXISTS stage.currency_usd(
    title VARCHAR(255) NOT NULL,
    rate float,
    date date NOT NULL
);

CREATE TABLE IF NOT EXISTS stage.currency_rub(
    title VARCHAR(255) NOT NULL,
    rate float,
    date date NOT NULL
);

CREATE TABLE IF NOT EXISTS stage.currency_kzt(
    currency VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    rate float,
    quantity int,
    index VARCHAR(255),
    change float,
    date date NOT NULL
);

