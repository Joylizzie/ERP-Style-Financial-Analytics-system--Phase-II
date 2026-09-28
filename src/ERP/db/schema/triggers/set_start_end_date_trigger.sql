--This is to trigger a new fiscal period given a fiscal period
CREATE OR REPLACE FUNCTION set_start_end_date()
RETURNS TRIGGER AS $$
BEGIN
    NEW.start_date := make_date(NEW.fiscal_year, NEW.fiscal_month, 1);
    NEW.end_date := (make_date(NEW.fiscal_year, NEW.fiscal_month, 1) + INTERVAL '1 month - 1 day')::date;
    
    -- Always return NEW in a BEFORE trigger to save the changes
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trg_set_start_end_date
BEFORE INSERT OR UPDATE ON fiscal_periods
FOR EACH ROW
EXECUTE FUNCTION set_start_end_date();


