import logging
import psycopg
from pathlib import Path
from ERP.db import create_db_and_user
from ERP.db.db_utilities import connection_pool, run_sql, run_sql_file_autocommit, run_sql_file, copy_folder_db

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
    file_path = project_root_folder/"src"/"ERP"/"data"/"master_data"/"seed_data"
    copy_folder_db(ocean_pool, file_path)


if __name__ == '__main__':
    main()
