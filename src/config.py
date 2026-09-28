import os
from pathlib import Path
from datetime import date
from dotenv import load_dotenv

def str_to_bool(str:str):
    if str.lower() == "true":
        return True
    elif str.lower() == "false":
        return False
    raise ValueError(f"Must provide with true or false: {str}")

# 1. Dynamically locate the project root (where .env lives)
# This points to the folder containing config.py
BASE_DIR = Path(__file__).resolve().parent 
ENV_PATH = BASE_DIR / ".env"

# 2. Load the .env file once into os.environ
load_dotenv(dotenv_path=ENV_PATH)


# Postgres db and user for connection
pg_db_host = os.getenv("pg_host")
pg_db_port = os.getenv("pg_port")
pg_su_user = os.getenv("pg_su_username")
pg_su_pw = os.getenv("pg_su_pw")

ocean_user_pw = os.getenv("ocean_user_pw")


start_date = date.fromisoformat(os.getenv("start_date"))
end_date = date.fromisoformat(os.getenv("end_date"))

# Fresh start db, user, predefine_table_data
fresh_start = str_to_bool(os.getenv("fresh_start"))

# Add new customers, vendors, employee etc. each month
make_monthly_adj = str_to_bool(os.getenv("make_monthly_adj"))

# Number of new customer to gen 
initial_num_customer_to_gen = int(os.getenv("initial_num_customer_to_gen"))
initial_num_bus_customer_to_gen = int(os.getenv("initial_num_bus_customer_to_gen"))
initial_num_ind_customer_to_gen = int(os.getenv("initial_num_ind_customer_to_gen"))

