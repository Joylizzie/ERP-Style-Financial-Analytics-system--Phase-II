-- fiscal_periods already has start column; rename if you prefer is_period_closed
ALTER TABLE fiscal_periods RENAME COLUMN is_closed TO is_period_closed;

CREATE OR REPLACE FUNCTION check_period_not_closed()
RETURNS TRIGGER AS $$
DECLARE
    period_closed BOOLEAN;
BEGIN
    SELECT is_period_closed INTO period_closed
    FROM fiscal_periods
    WHERE start_date <= NEW.transaction_date AND end_date >= NEW.transaction_date;

    IF period_closed THEN
        RAISE EXCEPTION 'Cannot post: period containing % is closed', NEW.transaction_date;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_gl_no_post_to_closed_period
    BEFORE INSERT OR UPDATE ON gl_transactions
    FOR EACH ROW EXECUTE FUNCTION check_period_not_closed();