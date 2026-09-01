
class PeriodLifecycleService:

    def close_module_period(self, period_id: int, module_name: str, next_period_id: int, closed_by: str = "system"):
        """Universal close: closes this module for period N, opens it for period N+1.
        Applies identically to every subledger AND to GL."""

        # GL has one extra precondition: all subledgers for THIS period must already be closed
        if module_name == "general_ledger":
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT string_agg(s.module_name, ', ') FROM fiscal_period_module_status s
                    JOIN modules m ON m.module_name = s.module_name
                    WHERE s.period_id = %s AND m.module_type = 'subledger' AND s.status != 'closed'
                """, (period_id,))
                open_subledgers = cur.fetchone()[0]
                if open_subledgers:
                    raise PermissionError(f"Cannot close GL: subledgers still open: {open_subledgers}")

        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE fiscal_period_module_status
                SET status = 'closed', closed_at = now(), closed_by = %s, updated_at = now()
                WHERE period_id = %s AND module_name = %s
            """, (closed_by, period_id, module_name))

            cur.execute("""
                UPDATE fiscal_period_module_status
                SET status = 'open', opened_at = now(), updated_at = now()
                WHERE period_id = %s AND module_name = %s
            """, (next_period_id, module_name))
        self.conn.commit()

    def assert_postable(self, module_name: str, period_id: int):
        """Called before ANY posting (GL or subledger) — checks this exact
        (period, module) pair is the one currently open."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT status FROM fiscal_period_module_status
                WHERE period_id = %s AND module_name = %s
            """, (period_id, module_name))
            row = cur.fetchone()
            if row is None or row[0] != 'open':
                raise PermissionError(f"{module_name} period {period_id} is not open for posting")