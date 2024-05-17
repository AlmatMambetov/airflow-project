CREATE TABLE IF NOT EXISTS kolesa_parsing(
    mark VARCHAR(255) NOT NULL,
    model VARCHAR(255) NOT NULL,
    year INT,
    price decimal,
    description VARCHAR(2000),
    city VARCHAR(255),
    generation VARCHAR(255),
    body VARCHAR(255),
    engine_volume decimal,
    mileage decimal,
    unit VARCHAR(255),
    transmission VARCHAR(255),
    drive_unit VARCHAR(255),
    steering_wheel VARCHAR(255),
    color VARCHAR(255),
    is_customized BOOLEAN
)