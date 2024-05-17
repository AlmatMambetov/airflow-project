CREATE SCHEMA IF NOT EXISTS fact;

CREATE SCHEMA IF NOT EXISTS stage;

CREATE TABLE IF NOT EXISTS fact.transport_data(
    id SERIAL PRIMARY KEY,
    period date,
    transport_type varchar(50),
    category varchar(50),
    value_int int,
    value_float float
);

CREATE TEMP TABLE IF NOT EXISTS stage.temp_data(
    period date,
    transport_type varchar(50),
    category varchar(50),
    value_int int,
    value_float float
)