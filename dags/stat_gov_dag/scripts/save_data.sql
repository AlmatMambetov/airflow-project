CREATE OR REPLACE FUNCTION update_or_insert_data()
RETURNS VOID AS $$
    BEGIN
    IF EXISTS (SELECT 1 FROM fact.transport_data) THEN
        UPDATE fact.transport_data fct
        SET value_float = stg.value_float,
            value_int = stg.value_int
        FROM stage.temp_data stg
            WHERE fct.period = stg.period
            AND fct.category = stg.category
            AND fct.transport_type = stg.transport_type
            AND fct.value_float != stg.value_int;
    ELSE
        INSERT INTO fact.transport_data(period, transport_type, category, value_int, value_float)
        SELECT period, transport_type, category, value_int, value_float FROM stage.temp_data;
    END IF;

    END;
    $$ LANGUAGE plpgsql;


SELECT update_or_insert_data()
