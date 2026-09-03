import logging
import psycopg
from pathlib import Path
from ERP.db import create_db_and_user
from ERP.db.db_utilities import connection_pool, run_sql, run_sql_file_autocommit, run_sql_file, copy_file_to_db, copy_from_db_file, copy_folder_db
from ERP.utilities.random_customer import make_customer_names, make_customer_addresses
from ERP.utilities.file_io import create_csv

logger = logging.getLogger(__name__)
project_root_folder = Path().resolve()

def main():

    # TO create a new db and its onwer, need postgres db and postgres as user
    run_sql("postgres", "postgres", create_db_and_user.create_db_queries(), autocommit=True) #Create db and ocean_user-Owner

    # Create ocean connection pool for sql operations
    ocean_pool = connection_pool("localhost", "5432", "ocean_stream", "ocean_user")
    file_path = project_root_folder/"src"/"ERP"/"db"/"schema"/"tables"
    run_sql_file(ocean_pool, file_path, "03_create_schema.sql") # Create schema, set as default search_path
    ocean_pool.drain()
    run_sql_file(ocean_pool, file_path, "create_tables.sql") # Create empty tables
    file_path = project_root_folder/"src"/"ERP"/"db"/"schema"/"triggers" # create triggers
    logger.info(f'file path is {file_path}')
    run_sql_file(ocean_pool, file_path, "set_start_end_date_trigger.sql")
    file_path = project_root_folder/"src"/"ERP"/"data"/"master_data"/"predefined_table_data"
    copy_folder_db(ocean_pool, file_path)
    path_file_out = project_root_folder/"src"/"ERP"/"data"/"master_data"/"made_data_fr_seed_random"
    create_csv(make_customer_names, path_file_out/'010_customer_names.csv', 200)
    copy_file_to_db(ocean_pool, path_file_out/"010_customer_names.csv")
    sql_query = "select customer_id, firstname, surname from customer_names where customer_id not in (select customer_id from customer_addresses)"
    copy_from_db_file(ocean_pool, path_file_out/"011_customer_missing_addr.csv", sql_query)
    create_csv(make_customer_addresses, path_file_out/'012_customer_addresses.csv', path_file_out/"011_customer_missing_addr.csv")
    copy_file_to_db(ocean_pool, path_file_out/"012_customer_addresses.csv")


if __name__ == '__main__':
    main()
