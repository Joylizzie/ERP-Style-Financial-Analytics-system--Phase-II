def create_db_queries():
    return [""" SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = 'ocean_stream' 
                AND pid <> pg_backend_pid();"""
            
            , """drop database if exists ocean_stream;"""

            , """create database ocean_stream;"""

            , """DROP ROLE IF EXISTS ocean_user;"""

            , """CREATE USER ocean_user WITH PASSWORD 'stream'; """

            , """ALTER DATABASE ocean_stream OWNER TO ocean_user;"""]
