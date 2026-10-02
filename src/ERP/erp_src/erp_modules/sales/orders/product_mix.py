import logging
from typing import 
from ERP.db.db_utilities import run_sql
from ERP.db.ocean_pool import get_pool

logger = logging.get_logger(__name__)

class ProductMix():
    """find product mix, each product mix related weight in current year, month;
    if no product mix related weight in current year/month, generate weights untill
    current year,month with grwoth rates
    """
    def get_product_mix_lst(self, business_type_id):
        sql = """select  pm_id, product_id from product_mix where business_type_id = %s
                order by pm_id, product_id"""
        product_mix_lst = run_sql(sql, (business_type_id,))
        product_mix_dict = {}
        for (pm_id, product_id) in product_mix_lst:
            product_mix_dict.setdefault(pm_id, []).append(product_id)
        
        return product_mix_dict

    def _get_weights(self, fiscal_year:int, fiscal_month:int):
        """Query product mix related weight in fiscal year, fiscal_month"""
        sql = """select pm_id, weight
                 from product_mix_weights
                where fiscal_year = %s and fiscal_month = %s and business_type_id = %s
                order by pm_id"""
        params = (fiscal_year, fiscal_month) 
        product_mix_weights = run_sql(sql, params)
        return product_mix_weights


    def get_cum_weights(self, fiscal_year:int, fiscal_month:int, business_type_id):
        """Query product mix related cummulated weight in fiscal year, fiscal_month"""
        sql = """select pm_id, sum(weight) over (order by pm_id) as cum_weight
                 from product_mix_weights
                where fiscal_year = %s and fiscal_month = %s and business_type_id = %s
                order by pm_id"""
        params = (fiscal_year, fiscal_month, business_type_id) 
        product_mix_weights = run_sql(sql, params)
        if len(product_mix_weights) == 0:
            return self.gen_weights_until(fiscal_year, fiscal_month)

        return product_mix_weights
    
    def gen_weights_until(self, fiscal_year:int, fiscal_month:int):
        """If cannot find product mix related weight in current year, month, 
        query the latest year, month and generated related mix based on previous month"""
        sql = """select fiscal_year, fiscal_month
                from product_mix_weights
                where (fiscal_year, fiscal_month) < (%s, %s)
                order by (fiscal_year, fiscal_month) desc limit 1"""
        params = (fiscal_year, fiscal_month) 
        start_year_month = run_sql(sql, params)
        start_year, start_month = start_year_month[0]
        prev_weights = self._get_weights(start_year, start_month)
        cur_year, cur_month = start_year, start_month
        while (cur_year, cur_month) < (fiscal_year, fiscal_month):
            cur_year = start_year if start_month < 12 else start_year + 1
            cur_month = start_month % 12 + 1 
            cur_weights = self.gen_next_month_weights(prev_weights, cur_year, cur_month)
        return product_mix_weights 
    
    def gen_next_month_weights(self, prev_weights, cur_year, cur_month):
        pass