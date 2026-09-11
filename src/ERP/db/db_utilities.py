
import logging
import psycopg
from psycopg_pool import ConnectionPool
from ERP.db.ocean_pool import get_pool
from pathlib import Path
import gzip
import shlex
import subprocess

logger = logging.getLogger(__name__)


 # TO create a new db and its onwer, need postgres db and postgres as user
def run_sql_db_user(user, dbname, sql_queries, autocommit=False):
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

def drain_pool(pool:ConnectionPool=None):
    if pool is None:
        pool = get_pool()
    pool.drain()
      
# Operations in the new db, use this
def run_sql_file_autocommit(file_path, filename, pool=None):
    if pool is None:
        pool = get_pool()
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
def run_sql_file(file_path, filename, pool=None):
    if pool is None:
        pool = get_pool()
    
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

def copy_file_to_db(path_file_name:Path, pool:ConnectionPool=None):
    """Copy a file to Postgres with a pool of connections"""
    table_name, copy_sql = get_copy_sql(path_file_name)
    if pool is None:
        pool = get_pool()
    try:
        logger.info(f"Processing file '{path_file_name}' into table '{table_name}'")
        if path_file_name.name.endswith(".gz"):
            file_context = gzip.open(path_file_name, "r", encoding="utf-8")
        else:
            file_context = open(path_file_name, "r", encoding="utf-8")    

        with file_context as f:
            with pool.connection() as conn:
                with conn.cursor() as cur:
                    with cur.copy(copy_sql) as copy:
                        while chunk := f.read(65536):
                            copy.write(chunk)
                            
        logger.info(f"Successfully uploaded {path_file_name} to {table_name}")
            
    except Exception as e:
        logger.error(f"Error occurring during copy {path_file_name} into {table_name}: {e}")
        raise e

def copy_folder_db(folder_path:Path, pool:ConnectionPool=None):
    """ Copy files in a folder to Postgres"""
    if pool is None:
        pool = get_pool()
    files = sorted(folder_path.glob("*.csv"))
    for file in files:
        copy_file_to_db(file, pool)

def copy_from_db_file(path_file_name:Path, sql_query:str, pool:ConnectionPool=None):
    """Downloads data from the database using COPY TO STDOUT and writes it to a file using Connectionpool."""
    if pool is None:
        pool = get_pool()
    try:
        # Rule applied: Open the file first
        if path_file_name.name.endswith(".gz"):
            file_context = gzip.open(path_file_name, "wb")
        else:
            file_context = open(path_file_name, "wb")

        with file_context as f:    
            logger.info(f'Opened file {path_file_name} and opening connection to query db')
            with pool.connection() as conn:
                with conn.cursor() as cur:
                    copy_statement = f"COPY ({sql_query.rstrip(';')}) TO STDOUT WITH CSV HEADER"
                    with cur.copy(copy_statement) as copy:
                        for chunk in copy:
                            f.write(chunk)
                                
        logger.info(f"Successfully downloaded {path_file_name}")
            
    except Exception as e:
        logger.error(f"Error occurring during copy {path_file_name}: {e}")
        raise e