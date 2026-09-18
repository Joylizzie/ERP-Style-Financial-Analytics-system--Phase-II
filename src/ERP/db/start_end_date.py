
from ERP.db.ocean_pool import get_pool
from ERP.db.db_utilities import run_sql_get_from_db

def start_end_date(sql, *args):
    sql = """select fiscal_year, fiscal_period, start_date, end_date
            from fiscal_periods fp
            join fiscal_period_module_status fpms
            on (fp.fical_year, fp.fical_month) = (fpms.fical_year, fpms.fical_month)
            where fpms.module_name = % $  and fpms.is_closed=False
            """
    run_sql_get_from_db(sql, module_name)