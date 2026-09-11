import logging
import datetime
from pathlib import Path
from ERP.db.ocean_pool import create_pool
from ERP.db import create_db_and_user
from ERP.db.db_utilities import drain_pool, run_sql_db_user, run_sql_file_autocommit, run_sql_file, copy_file_to_db, copy_from_db_file, copy_folder_db
from ERP.utilities.random_customer import make_customer_names, make_customer_addresses
from ERP.utilities.file_io import create_csv
from ERP.erp_src.erp_modules.sales.orders.pre_sales_order import generate_value_tuples, _to_csv

logger = logging.getLogger(__name__)
project_root_folder = Path().resolve()

def main():

    # TO create a new db and its onwer, need postgres db and postgres as user
    run_sql_db_user("postgres", "postgres", create_db_and_user.create_db_queries(), autocommit=True) #Create db and ocean_user-Owner

    # Create ocean connection pool for sql operations
    # ocean_pool = connection_pool("localhost", "5432", "ocean_stream", "ocean_user")
    file_path = project_root_folder/"src"/"ERP"/"db"/"schema"/"tables"
    create_pool()
    run_sql_file(file_path, "03_create_schema.sql") # Create schema, set as default search_path
    drain_pool()
    run_sql_file(file_path, "create_tables.sql") # Create empty tables
    file_path = project_root_folder/"src"/"ERP"/"db"/"schema"/"triggers" # create triggers
    logger.info(f'file path is {file_path}')
    run_sql_file(file_path, "set_start_end_date_trigger.sql")
    file_path = project_root_folder/"src"/"ERP"/"data"/"master_data"/"predefined_table_data"
    copy_folder_db(file_path)
    path_file_out = project_root_folder/"src"/"ERP"/"data"/"master_data"/"made_data_fr_seed_random"
    path_file_out.mkdir(parents=True, exist_ok=True)
    create_csv(make_customer_names, path_file_out/'010_customer_names.csv', 500)
    copy_file_to_db(path_file_out/"010_customer_names.csv")
    sql_query = "select customer_id, firstname, surname from customer_names where customer_id not in (select customer_id from customer_addresses)"
    copy_from_db_file(path_file_out/"011_customer_missing_addr.csv", sql_query)
    create_csv(make_customer_addresses, path_file_out/'012_customer_addresses.csv', path_file_out/"011_customer_missing_addr.csv")
    copy_file_to_db(path_file_out/"012_customer_addresses.csv")
    n_sample_b, n_sample_i = 100, 198
    start_date = datetime.date(2021, 3, 1)
    end_date = datetime.date(2021, 7, 31)
    # Generate number n sample of customer_ids for sales orders 
    _to_csv(n_sample_b, n_sample_i, start_date, end_date, path_file_out)


if __name__ == '__main__':
    main()
