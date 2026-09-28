-- fiscal_periods already has start column; rename if you prefer is_period_closed

CREATE OR REPLACE FUNCTION check_period_not_closed()
RETURNS TRIGGER AS $$
DECLARE
    period_closed BOOLEAN;
BEGIN
    SELECT is_closed INTO period_closed
    FROM fiscal_period_module_status
    WHERE  fiscal_year = NEW.fiscal_year
     AND fiscal_month =  NEW.fiscal_month
     AND module_name = NEW.module_name;

    IF period_closed THEN
        RAISE EXCEPTION 'Cannot post: period containing % is closed', (NEW.fiscal_year, NEW.fiscal_month);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sa_or_no_post_to_closed_period
    BEFORE INSERT OR UPDATE ON sales_orders
    FOR EACH ROW EXECUTE FUNCTION check_period_not_closed();

CREATE TRIGGER trg_sa_in_no_post_to_closed_period
    BEFORE INSERT OR UPDATE ON sales_invoices
    FOR EACH ROW EXECUTE FUNCTION check_period_not_closed();

CREATE TRIGGER trg_ar_in_no_post_to_closed_period
    BEFORE INSERT OR UPDATE ON ar_invoice
    FOR EACH ROW EXECUTE FUNCTION check_period_not_closed();

CREATE TRIGGER trg_ar_re_no_post_to_closed_period
    BEFORE INSERT OR UPDATE ON ar_receipt
    FOR EACH ROW EXECUTE FUNCTION check_period_not_closed();

CREATE TRIGGER trg_pu_or_no_post_to_closed_period
    BEFORE INSERT OR UPDATE ON purchase_orders
    FOR EACH ROW EXECUTE FUNCTION check_period_not_closed();

CREATE TRIGGER trg_ap_in_no_post_to_closed_period
    BEFORE INSERT OR UPDATE ON ap_invoice
    FOR EACH ROW EXECUTE FUNCTION check_period_not_closed();

CREATE TRIGGER trg_ap_pa_no_post_to_closed_period
    BEFORE INSERT OR UPDATE ON ap_payment
    FOR EACH ROW EXECUTE FUNCTION check_period_not_closed();

CREATE TRIGGER trg_gl_no_post_to_closed_period
    BEFORE INSERT OR UPDATE ON journal_entry
    FOR EACH ROW EXECUTE FUNCTION check_period_not_closed();