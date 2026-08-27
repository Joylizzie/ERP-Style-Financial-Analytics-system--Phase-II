import logging
import psycopg
from pathlib import Path
from ERP.db import create_db_and_user
from ERP.db.db_utilities import run_sql, run_sql_file#, run_psql_file

logger = logging.getLogger(__name__)
project_root_folder = Path().resolve()

def main():

    # TO create a new db and its onwer, need postgres db and postgres as user
    run_sql("postgres", "postgres", create_db_and_user.create_db_queries(), autocommit=True) #Create db and ocean_user-Owner
    # Operations in the new db, use this
    file_path = project_root_folder/"src"/"ERP"/"db"/"schema"/"tables"
    run_sql_file("ocean_user", "ocean_stream", file_path, "03_create_schema.sql") # Create schema, set as default search_path
    run_sql_file("ocean_user", "ocean_stream", file_path, "create_tables.sql") # Create empty tables
    file_path = project_root_folder/"src"/"ERP"/"db"/"schema"/"triggers" # create triggers
    logger.info(f'file path is {file_path}')
    run_sql_file("ocean_user", "ocean_stream", file_path, "set_start_end_date_trigger.sql")
    # run_psql_file("ocean_user", "ocean_stream", file_path, "create_table_values.sql")


if __name__ == '__main__':
    main()
