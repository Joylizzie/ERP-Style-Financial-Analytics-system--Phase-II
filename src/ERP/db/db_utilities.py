
import logging
import psycopg
from psycopg_pool import ConnectionPool
from pathlib import Path
import shlex
import subprocess

logger = logging.getLogger(__name__)

def connection_pool(host, port, dbname, user, min_size=2, max_size=10, pgpass_path=None):
    conn_info = f"host={host} port={port} dbname={dbname} user={user}"
    if pgpass_path:
        logger.info(f'Find .pgpass file {pgpass_path}')
        conn_info += f"passfile={pgpass_path}"
    try:
        pool = ConnectionPool(conn_info, min_size=min_size, max_size=max_size)
        logger.info(f'connection pool created {pool}')
        return pool
    except Exception as e:
        logger.error(f"Failed to initialize connection pool for {user}@{host}: {e}")


 # TO create a new db and its onwer, need postgres db and postgres as user
def run_sql(user, dbname, sql_queries, autocommit=False):
    conn = psycopg.connect(host="localhost", port="5432", dbname=dbname, user=user)
    conn.autocommit = autocommit
    try:
        with conn.cursor() as cur:
            for sql_query in sql_queries:
                conn.execute(sql_query)
        if not autocommit:
            conn.commit()    
        conn.close()
    except: 
        logger.error
        if conn:
           conn.close()
        raise 
    
# Operations in the new db, use this
def run_sql_file_autocommit(pool:ConnectionPool, file_path, filename):
    try:
        sql = (file_path / filename).read_text()
        conn = pool.getconn()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(sql)
            
    except: 
        logger.error
        conn.close()
        raise 
    finally:
    # Always call putconn; the pool will see it's closed and discard it
        pool.putconn(conn) 

    logger.info(f'Executed sql in {file_path/filename}')

# Operations in the new db, use this
def run_sql_file(pool:ConnectionPool, file_path, filename):
    try:
        sql = (file_path / filename).read_text()
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
    except: 
        logger.error
        raise 
    logger.info(f'Executed sql in {file_path/filename}')

def run_psql_file(user:str, dbname:str, file_path:Path, file_name:Path):
    """Using psql to upload file to Postgres"""
    file_path_name = f'{file_path/file_name}'
    logger.info(file_path_name)
    command = shlex.split(f'psql --host=localhost -U {user}  --dbname={dbname} -a -f {file_path_name}')

    # Run the command
    result = subprocess.run(command, capture_output=True, text=True)

    # Check if it worked
    if result.returncode == 0:
        logger.info("psql connected:", result.stdout)
    else:
        logger.error("psql is not able to connect:", result.stderr)

def get_copy_sql(path_file_name:Path):
    """Based on legacy file which copies table vaules to Postgres, retrieve table name and rewrite copy command"""
    table_name = path_file_name.stem[4:]
    with open(path_file_name, "r", encoding="utf-8") as file:
        col_str = file.readline().strip()
    sql_str = f"COPY {table_name}({col_str}) FROM STDIN WITH DELIMITER ',' CSV HEADER;"
    return [table_name, sql_str]

def copy_file_db(pool:ConnectionPool, path_file_name:Path):
    """Copy a file to Postgres with a pool of connections"""
    table_name, copy_sql = get_copy_sql(path_file_name)

    try:
        logger.info(f"Processing file '{path_file_name}' into table '{table_name}'")
            
        with pool.connection() as conn:
            with conn.cursor() as cur:
                with open(path_file_name, "r", encoding="utf-8") as f:
                    with cur.copy(copy_sql) as copy:
                        while chunk := f.read(65536):
                            copy.write(chunk)
                            
        logger.info(f"Successfully uploaded {path_file_name} to {table_name}")
            
    except Exception as e:
        logger.error(f"Error occurring during copy {path_file_name} into {table_name}: {e}")
        raise e

def copy_folder_db(pool:ConnectionPool, folder_path:Path):
    """ Copy files in a folder to Postgres"""
    files = sorted(folder_path.glob("*.csv"))
    for file in files:
        copy_file_db(pool, file)