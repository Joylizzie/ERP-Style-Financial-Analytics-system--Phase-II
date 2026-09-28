from ERP.db.db_connection import connection_pool

pool = None
# Create ocean connection pool for sql operations
def create_pool():
    global pool
    pool = connection_pool("localhost", "5432", "ocean_stream", "ocean_user")

def get_pool():
    return pool