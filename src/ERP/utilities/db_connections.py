import logging
import psycopg

logger = logging.getLogger(__name__)

class DBConnection:
    def __init__( self,host: str, port: str, db: str, user: str):
        self.db = db
        self.user = user
        self.host = host
        self.port = port

    def get_psycopg(self):
        conn = psycopg.connect(
            host=self.host,
            port=self.port,
            dbname=self.db,
            user=self.user,
        )
        logger.info('Connected Postgres with psycopg')
        return conn


    def get_psql_args(self):
        conn = [
            "psql",
            "-h", self.host,
            '-p', self.port,
            "-d", self.db,
            "-U", self.user,
        ]
        logger.info('Connected Postgres with psql')
        return conn


if __name__ == "__main__":
    logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s",        )
 
    sol = DBConnection(host="localhost", port="5432", db="ocean_stream", user="ocean_user")
    sol.get_psql_args()
    sol.get_psycopg()