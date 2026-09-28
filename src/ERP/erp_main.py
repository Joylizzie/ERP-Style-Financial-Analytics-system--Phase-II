import logging
from datetime import date
import calendar
from pathlib import Path
from ERP.db.ocean_pool import create_pool
from ERP.db import create_db_and_user
from ERP.db.db_utilities import drain_pool, run_sql_db_user, run_sql_file_autocommit, run_sql_file, copy_file_to_db, copy_from_db_file, copy_folder_db, copy_generator_tup_to_db
from ERP.utilities.random_customer import make_customer_names, make_customer_addresses
from ERP.utilities.file_io import create_csv
import config as conf
# from config import start_date, end_date, fresh_start, make_monthly_adj, initial_num_customer_to_gen
from ERP.erp_src.erp_modules.sales.orders.pre_sales_order import sales_order_value_tups_gen
import ERP.erp_src.erp_modules.sys_ops.fiscal_period as fs

logger = logging.getLogger(__name__)
project_root_folder = Path().resolve()

def initialize_pg_db():
   # TO create a new db and its onwer, need postgres db and postgres as user
    run_sql_db_user("postgres", "postgres", create_db_and_user.create_db_queries(), autocommit=True)

    # Create ocean connection pool for sql operations
    file_path = project_root_folder/"src"/"ERP"/"db"/"schema"/"tables"
    create_pool()
    run_sql_file(file_path, "03_create_schema.sql") # Create schema, set as default search_path
    drain_pool()
    run_sql_file(file_path, "create_tables.sql") # Create empty tables

    file_path = project_root_folder/"src"/"ERP"/"db"/"schema"/"triggers" # create triggers
    logger.info(f'file path is {file_path}')
    run_sql_file(file_path, "set_start_end_date_trigger.sql")
    run_sql_file(file_path, "fiscal_period_open_close_trigger.sql")
    file_path = project_root_folder/"src"/"ERP"/"data"/"master_data"/"predefined_table_data"
    copy_folder_db(file_path)

def increment_month(source_date:date):
    mon = source_date.month
    year = source_date.year
    return date((year if mon < 12 else year + 1), (mon % 12 + 1), 1)

def gen_data():
    cur_date = conf.start_date
    while cur_date < conf.end_date:
        logger.info(f'')
        logger.info(f"About to generate data for mon {cur_date}")
        gen_data_for_month(cur_date.year, cur_date.month)
        cur_date = increment_month(cur_date)

def monthly_adjs(year, month):
    if conf.make_monthly_adj:
        logger.info("Monthly adjustments not implemented!")
    return

def gen_everymon_data(year, month):
    # Generate sales_orders by customer_ids in "year, month"
    cur_start_date = date(year, month, 1)
    cur_end_date = date(year, month, calendar.monthrange(year, month)[1]) # the end of the month
    sales_order_ids_gen = sales_order_value_tups_gen([conf.initial_num_bus_customer_to_gen,\
           conf.initial_num_ind_customer_to_gen], cur_start_date, cur_end_date)
    table_cols = ['company_code', 's_order_date', 'fiscal_year', 'fiscal_month', 'customer_id']
    logger.info(f"start to upload {year}-{month} sales_order_ids ")
    copy_generator_tup_to_db(sales_order_ids_gen, "sales_orders", table_cols)
    logger.info(f"Finished uploading {conf.initial_num_bus_customer_to_gen} and {conf.initial_num_ind_customer_to_gen} in {year}-{month} sales_order_ids")

def gen_data_for_month(year, month):
    """ Create the fiscal period, module status;
        do all the transactions and produce Transaction_list, TB, Balance Sheet, PL
        Then close the fiscal perod
    """
    fs.ensure_create_fiscal_period(year, month)
    
    if conf.fresh_start and (conf.start_date.year == year and conf.start_date.month == month):
        # generate initial data for customers
        path_file_out = project_root_folder/"src"/"ERP"/"data"/"master_data"/"made_data_fr_seed_random"
        path_file_out.mkdir(parents=True, exist_ok=True)
        create_csv(make_customer_names, path_file_out/'010_customer_names.csv', conf.initial_num_customer_to_gen)
        copy_file_to_db(path_file_out/"010_customer_names.csv")
        sql_query = "select customer_id, firstname, surname from customer_names where customer_id not in (select customer_id from customer_addresses)"
        copy_from_db_file(path_file_out/"011_customer_missing_addr.csv", sql_query)
        create_csv(make_customer_addresses, path_file_out/'012_customer_addresses.csv', path_file_out/"011_customer_missing_addr.csv")
        copy_file_to_db(path_file_out/"012_customer_addresses.csv")
        # Generate number n sample of customer_ids for sales orders 
        # _to_csv(conf.initial_num_bus_customer_to_gen, conf.initial_num_ind_customer_to_gen, conf.start_date, conf.end_date, path_file_out)

    elif conf.make_monthly_adj:
        monthly_adjs(year, month)
    gen_everymon_data(year, month)  

    fs.close_fiscal_period(year, month)

def main():
    if conf.fresh_start:
        initialize_pg_db()
    gen_data()





# def main():

#     # TO create a new db and its onwer, need postgres db and postgres as user
#     run_sql_db_user("postgres", "postgres", create_db_and_user.create_db_queries(), autocommit=True) #Create db and ocean_user-Owner

#     # Create ocean connection pool for sql operations
#     # ocean_pool = connection_pool("localhost", "5432", "ocean_stream", "ocean_user")
#     file_path = project_root_folder/"src"/"ERP"/"db"/"schema"/"tables"
#     create_pool()
#     run_sql_file(file_path, "03_create_schema.sql") # Create schema, set as default search_path
#     drain_pool()
#     run_sql_file(file_path, "create_tables.sql") # Create empty tables
#     file_path = project_root_folder/"src"/"ERP"/"db"/"schema"/"triggers" # create triggers
#     logger.info(f'file path is {file_path}')
#     run_sql_file(file_path, "set_start_end_date_trigger.sql")
#     file_path = project_root_folder/"src"/"ERP"/"data"/"master_data"/"predefined_table_data"
#     copy_folder_db(file_path)
#     path_file_out = project_root_folder/"src"/"ERP"/"data"/"master_data"/"made_data_fr_seed_random"
#     path_file_out.mkdir(parents=True, exist_ok=True)
#     create_csv(make_customer_names, path_file_out/'010_customer_names.csv', 500)
#     copy_file_to_db(path_file_out/"010_customer_names.csv")
#     sql_query = "select customer_id, firstname, surname from customer_names where customer_id not in (select customer_id from customer_addresses)"
#     copy_from_db_file(path_file_out/"011_customer_missing_addr.csv", sql_query)
#     create_csv(make_customer_addresses, path_file_out/'012_customer_addresses.csv', path_file_out/"011_customer_missing_addr.csv")
#     copy_file_to_db(path_file_out/"012_customer_addresses.csv")
#     n_sample_b, n_sample_i = 100, 198
#     start_date = datetime.date(2021, 3, 1)
#     end_date = datetime.date(2021, 7, 31)
#     # Generate number n sample of customer_ids for sales orders 
#     _to_csv(n_sample_b, n_sample_i, start_date, end_date, path_file_out)



if __name__ == '__main__':
    main()
