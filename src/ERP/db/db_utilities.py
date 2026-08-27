
import logging
import psycopg
from pathlib import Path
import subprocess

logger = logging.getLogger(__name__)
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
def run_sql_file(user, dbname, file_path, filename, autocommit=False):
    sql = (file_path / filename).read_text()
    conn = psycopg.connect(host="localhost", port="5432", dbname=dbname, user=user)
    conn.autocommit = autocommit
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        if not autocommit:
            conn.commit()    
        conn.close()
    except: 
        logger.error
        if conn:
           conn.close()
        raise 
    logger.info(f'Executed sql in {file_path/filename}')

# def run_psql_file(user, dbname, file_path, file_name):
#     file_path_name = f'{file_path/file_name}'
#     command = ["psql", "--host", "localhost", "--port", "5432",  "-U", user, "-d", dbname, "-a", "-f", file_path_name]


#     # Run the command
#     result = subprocess.run(command, capture_output=True, text=True)

#     # Check if it worked
#     if result.returncode == 0:
#         print("Success:", result.stdout)
#     else:
#         print("Error:", result.stderr)
