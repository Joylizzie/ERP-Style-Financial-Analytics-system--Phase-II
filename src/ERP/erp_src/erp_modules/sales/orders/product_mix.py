import logging
from typing import List
import random  
from ERP.db.db_utilities import run_sql_get,insert_small_data_to_db
from ERP.db.ocean_pool import get_pool
import config as conf 

logger = logging.getLogger(__name__)

class ProductMix():
    """find product mix, each product mix related weight in current year, month;
    if no product mix related weight in current year/month, generate weights untill
    current year,month with grwoth rates
    """
    def get_product_mix_lst(self, business_type_id:int)->dict:
        sql = """select  pm_id, product_id from product_mix where business_type_id = %s
                order by pm_id, product_id"""
        product_mix_lst = run_sql_get(sql, (business_type_id,))
        product_mix_dict = {}
        for (pm_id, product_id) in product_mix_lst:
            product_mix_dict.setdefault(pm_id, []).append(product_id)
        
        return product_mix_dict

    def _get_weights(self, fiscal_year:int, fiscal_month:int):
        """Query product_mix_id related weight in fiscal year, fiscal_month"""
        sql = """select pm_id, weight
                 from product_mix_weights
                where fiscal_year = %s and fiscal_month = %s 
                order by pm_id"""
        params = (fiscal_year, fiscal_month) 
        product_mix_weights = run_sql_get(sql, params)
        return product_mix_weights


    def get_cum_weights(self, fiscal_year:int, fiscal_month:int, business_type_id):
        """Query product_mix related cummulated weight in fiscal year, fiscal_month"""
        sql = """
            select pm_id, sum(weight) over (order by pm_id) as cum_weight
            from product_mix_weights
            where fiscal_year = %s and fiscal_month = %s 
            and exists (select 1 from product_mix where pm_id = product_mix_weights.pm_id and business_type_id = %s)
            order by pm_id"""
        params = (fiscal_year, fiscal_month, business_type_id) 
        product_mix_weights = run_sql_get(sql, params)
        if len(product_mix_weights) == 0:
            self.gen_weights_until(fiscal_year, fiscal_month)
            product_mix_weights = run_sql_get(sql, params)
        return product_mix_weights
    
    def gen_weights_until(self, fiscal_year:int, fiscal_month:int):
        """If cannot find product_mix related weight in current year, month, 
        query the latest (year, month) and generated related mix based on previous (fiscal_year, fiscal_month)"""
        sql = """select fiscal_year, fiscal_month
                from product_mix_weights
                where (fiscal_year, fiscal_month) < (%s, %s)
                order by (fiscal_year, fiscal_month) desc limit 1"""
        params = (fiscal_year, fiscal_month) 
        start_year_month = run_sql_get(sql, params)
        start_year, start_month = start_year_month[0]
        prev_weights = self._get_weights(start_year, start_month)
        cur_year, cur_month = start_year, start_month
        while (cur_year, cur_month) < (fiscal_year, fiscal_month):
            cur_year = start_year if start_month < 12 else start_year + 1
            cur_month = start_month % 12 + 1 
            prev_weights = self.gen_next_month_weights(prev_weights, cur_year, cur_month)

    
    def gen_next_month_weights(self, prev_weights, cur_year, cur_month):
        """Generate product_mix new weight from old weights in a random uniformed range from config file"""
        low = conf.product_mix_random_mult_lower
        high = conf.product_mix_random_mult_higher
        new_weights = [(pm_id, random.uniform(low, high) * weight, cur_year, cur_month) for (pm_id, weight) in prev_weights]
        sql = """INSERT INTO product_mix_weights (pm_id, weight, fiscal_year, fiscal_month)
                  VALUES (%s, %s, %s, %s)
            """
        insert_small_data_to_db(sql, new_weights)
        return  [(pm_id, weight) for (pm_id, weight, _, _) in new_weights]
        