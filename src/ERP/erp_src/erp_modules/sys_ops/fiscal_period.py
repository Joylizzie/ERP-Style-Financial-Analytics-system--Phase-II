import logging
# import psycopg
from typing import List, Any
# from psycopg_pool import ConnectionPool
from datetime import date
from ERP.db.ocean_pool import get_pool

logger = logging.getLogger(__name__)

def ensure_create_fiscal_period(year, month):
    pool = get_pool()
    sql_fiscal_periods = """
            INSERT INTO fiscal_periods (fiscal_year, fiscal_month)
            VALUES (%s, %s)
            ON CONFLICT (fiscal_year, fiscal_month) DO NOTHING;
            """
    sql_fiscal_period_module_status = """
            INSERT INTO fiscal_period_module_status (fiscal_year, fiscal_month, module_name)
            SELECT %s, %s, module_name from modules
            ON CONFLICT  (fiscal_year, fiscal_month, module_name) DO NOTHING;        
            """
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_fiscal_periods, (year, month))
            cur.execute(sql_fiscal_period_module_status, (year, month))

def close_fiscal_period(year, month):
    pool = get_pool()
    sql = """
            UPDATE fiscal_period_module_status
            SET is_closed = True, 
                closed_at = NOW(),
                updated_at = NOW(),
                closed_by = 'system_user'
                
            WHERE fiscal_year = %s AND fiscal_month = %s
            """
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (year, month))

# def assert_postable(self, module_name: str, period_id: int):
#     """Called before ANY posting (GL or subledger) — checks this exact
#     (period, module) pair is the one currently open."""
#     with self.conn.cursor() as cur:
#         cur.execute("""
#             SELECT status FROM fiscal_period_module_status
#             WHERE period_id = %s AND module_name = %s
#         """, (period_id, module_name))
#         row = cur.fetchone()
#         if row is None or row[0] != 'open':
#             raise PermissionError(f"{module_name} period {period_id} is not open for posting")