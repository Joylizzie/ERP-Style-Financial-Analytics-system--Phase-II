import random
import logging
import os
from pathlib import Path
import csv
from datetime import datetime
from ERP.db.db_utilities import *
from ERP.utilities.random_customer import *

logger = logging.getLogger(__name__)

project_root_folder = Path.resolve()
made_data_fr_seed_random_folder = os.makedirs(project_root_folder/"src"/"ERP"/"data"/"master_data"/"made_data_fr_seed_random", exist_ok=True)

# choose random date bwtween start and end date
def randomdate(start_date, end_date):
    # calculate time between start_date and end_date, then convert the time to days
    days_between_dates = (end_date - start_date).days
    # select random day in above days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    return random_date


def get_cust_ids_by_type(conn):
    "Get a list of customer_ids by business_type and save in different csv files"
    business_types = get_business_types()
    cust_ids_bt = {}
    sql = """select customer_id from customer_names 
            where business_type_id= %s and company_code='US001';"""
    for bt in business_types:
        with conn.cursor() as curs:
            curs.execute("set search_path to ocean_stream;")
            curs.execute(sql, (bt,))  #cursor closed after the execute action
            cust_ids = curs.fetchall()# a list of tuples
            cust_ids_bt[bt].append(cust_ids)

        with open(os.path.join(made_data_fr_seed_random_folder, f'cust_ids_{bt}'), 'w') as write_obj:
            csv_writer = csv.writer(write_obj)
            csv_writer.writerow(['customer_id']) # write header        
            csv_writer.writerows(cust_ids)
    logger.info(f'Customer_ids by type is written in {made_data_fr_seed_random_folder}')    
    return cust_ids_bt  

def generate_value_tuples(n_sample_b, n_sample_i, start_date, end_date,conn):
    cust_ids_b, cust_ids_i = get_cust_ids_by_type(conn)            
    b_cust_ids_sample = random.sample(cust_ids_b, n_sample_b)
    i_cust_ids_sample = random.sample(cust_ids_i, n_sample_i)
    random_cust_ids = b_cust_ids_sample + i_cust_ids_sample
    n = n_sample_b + n_sample_i
   
    t = [('US001',randomdate(start_date, end_date),*random_cust_ids[i]) for i in range(n)]
    return t

       
# generate sales order values and save in csv file, then upload to db from psql which is quicker comparing to below way.
def _to_csv(n_sample_b, n_sample_i, start_date, end_date,conn, outfile):
    tups = generate_value_tuples(n_sample_b, n_sample_i, start_date, end_date,conn)
    with open(os.path.join(made_data_fr_seed_random_folder, outfile), 'w') as write_obj:
        csv_writer = csv.writer(write_obj)
        csv_writer.writerow(['company_code', 's_order_date', 'customer_id']) # write header
        n = n_sample_b + n_sample_i
        for i in range(n):
            csv_writer.writerow(tups[i])
        logger.info(f'{n_sample_b}  and {n_sample_i} pre_sales_orders writing')
