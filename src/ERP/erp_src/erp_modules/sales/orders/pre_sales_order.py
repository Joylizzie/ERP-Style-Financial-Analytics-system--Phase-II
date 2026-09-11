import random
import logging
import os
from pathlib import Path
import csv
import datetime
from ERP.db.db_utilities import *
from ERP.db.ocean_pool import get_pool
from ERP.utilities.file_io import create_csv
from ERP.utilities.random_customer import get_business_types

logger = logging.getLogger(__name__)

# choose random date bwtween start and end date
def randomdate(start_date, end_date):
    # calculate time between start_date and end_date, then convert the time to days
    days_between_dates = (end_date - start_date).days
    # select random day in above days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    return random_date


def get_cust_ids_by_type():
    "Get a list of customer_ids by business_type and save in different csv files"
    business_types = get_business_types()
    cust_ids_lst = []
    sql = """select customer_id from customer_names 
            where business_type_id= %s and company_code='US001';"""
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            for bt in business_types:
                cur.execute(sql, (bt,))  #cursor closed after the execute action
                cust_ids = cur.fetchall()# a list of tuples
                cust_ids_lst.append(cust_ids)

    #             with open(made_data_fr_seed_random_folder/(f'cust_ids_{bt}.csv'), 'w') as write_obj:
    #                 csv_writer = csv.writer(write_obj)
    #                 csv_writer.writerow(['customer_id']) # write header        
    #                 csv_writer.writerows(cust_ids)
    # logger.info(f'Customer_ids by type is written in {made_data_fr_seed_random_folder}')    
    return cust_ids_lst  

def generate_value_tuples(n_sample_b, n_sample_i, start_date, end_date):
    cust_ids_b, cust_ids_i = get_cust_ids_by_type()            
    b_cust_ids_sample = random.sample(cust_ids_b, n_sample_b)
    i_cust_ids_sample = random.sample(cust_ids_i, n_sample_i)
    t_b = [('US001',randomdate(start_date, end_date),*b_cust_ids_sample[i]) for i in range(n_sample_b)]
    t_i = [('US001',randomdate(start_date, end_date),*i_cust_ids_sample[i]) for i in range(n_sample_i)]
    return t_b, t_i

       
# generate sales order values and save in csv file, then upload to db from psql which is quicker comparing to below way.
def _to_csv(n_sample_b, n_sample_i, start_date, end_date, path):
    t_b, t_i = generate_value_tuples(n_sample_b, n_sample_i, start_date, end_date)
    with open(path/f'pre_sales_orders_business.csv', 'w') as write_obj:
        csv_writer = csv.writer(write_obj)
        csv_writer.writerow(['company_code', 's_order_date', 'customer_id']) # write header
        for i in range(n_sample_b):
            csv_writer.writerow(t_b[i])

    with open(path/f'pre_sales_orders_individul.csv', 'w') as write_obj:
        csv_writer = csv.writer(write_obj)
        csv_writer.writerow(['company_code', 's_order_date', 'customer_id']) # write header
        for j in range(n_sample_i):
            csv_writer.writerow(t_i[j])
    logger.info(f'{n_sample_b}  and {n_sample_i} pre_sales_orders writing')

