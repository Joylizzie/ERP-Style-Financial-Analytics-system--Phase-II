import logging
from psycopg_pool import ConnectionPool


logger = logging.getLogger(__name__)

def connection_pool(host, port, dbname, user, min_size=2, max_size=10, pgpass_path=None)-> ConnectionPool:
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