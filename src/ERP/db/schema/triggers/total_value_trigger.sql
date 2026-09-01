CREATE OR REPLACE FUNCTION calculate_total_value()
RETURNS TRIGGER AS $$
BEGIN
    -- Set the column based on other columns in the inserted row
    NEW.total_value := NEW.price * NEW.quantity;
    
    -- Always return NEW in a BEFORE trigger to save the changes
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trg_products_total_value
BEFORE INSERT ON products
FOR EACH ROW
EXECUTE FUNCTION calculate_total_value();
