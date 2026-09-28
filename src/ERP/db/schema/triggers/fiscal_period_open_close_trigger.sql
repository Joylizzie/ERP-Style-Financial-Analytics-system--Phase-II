-- fiscal_periods already has start column; rename if you prefer is_period_closed

CREATE OR REPLACE FUNCTION check_period_not_closed()
RETURNS TRIGGER AS $$
DECLARE
    period_closed BOOLEAN;
BEGIN
    SELECT is_closed INTO period_closed
    FROM fiscal_period_module_status
    WHERE  fiscal_year = EXTRACT(YEAR FROM NEW.s_order_date)
     AND fiscal_month = EXTRACT(month FROM NEW.s_order_date)
     AND module_name = NEW.module_name;

    IF period_closed THEN
        -- RAISE EXCEPTION 'Cannot post: period containing % is closed', NEW.transaction_date;
        RAISE EXCEPTION 'Cannot post: period containing % is closed', NEW.s_order_date;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_so_no_post_to_closed_period
    BEFORE INSERT OR UPDATE ON sales_orders
    FOR EACH ROW EXECUTE FUNCTION check_period_not_closed();

-- CREATE TRIGGER trg_gl_no_post_to_closed_period
--     BEFORE INSERT OR UPDATE ON gl_transactions
--     FOR EACH ROW EXECUTE FUNCTION check_period_not_closed();