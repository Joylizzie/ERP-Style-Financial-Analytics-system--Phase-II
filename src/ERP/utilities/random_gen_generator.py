import logging
from typing import List
from pathlib import Path
import random
import csv
import string
import os

logger = logging.getLogger(__name__)

random.seed(3.1415)

project_root_folder = Path().resolve()
seed_data_folder = project_root_folder/"src"/"ERP"/"data"/"master_data"/"seed_data"
made_data_fr_seed_random_folder = project_root_folder/"src"/"ERP"/"data"/"master_data"/"made_data_fr_seed_random"

def get_random_data_from_seed(input_file:Path, col_lst:List[str], weight_col:str):
    new_row_lst, weight_lst = [], []
    with open(input_file, 'r') as read_obj:
        csv_reader = csv.DictReader(read_obj)
        for row in csv_reader:
            new_row_lst.append({col:row[col] for col in col_lst})
            weight_lst.append(float(row[weight_col]))
    return (new_row_lst, weight_lst)

def make_random_cities(num):
    """Pull randomly (weighted by population) num rows with specified cols - city, zip_code, area_code  from input file"""
    input_file = seed_data_folder/"cities.csv"
    col_lst = ['city', 'zip_code', 'area_code']
    rows, weights = get_random_data_from_seed(input_file, col_lst, weight_col="population")
    for _ in range(num):
        yield random.choices(rows, weights=weights, k=1)[0]
    # random_cities = random.choices(rows,  weights=weights, k=num)
    # return random_cities

def make_random_streets(num):
    """Pull randomly (weighted by column weight) num rows with specified cols - street_name  from input file"""
    input_file = seed_data_folder/"street_names.csv"
    col_lst = ['street_name']
    rows, weights = get_random_data_from_seed(input_file, col_lst, weight_col="weight")
    for _ in range(num):
        yield random.choices(rows, weights=weights, k=1)[0]
    # random_streets = random.choices(rows,  weights=weights, k=num)
    # return random_streets

def make_random_surnames(num):
    """Pull randomly (weighted by column weight) num rows with specified cols - surname  from input file"""
    input_file = seed_data_folder/"surnames.csv"
    col_lst = ['surname']
    rows, weights = get_random_data_from_seed(input_file, col_lst, weight_col="weight")
    for _ in range(num):
        yield random.choices(rows, weights=weights, k=1)[0]
    # random_surnames = random.choices(rows, weights=weights, k=num)
    # return random_surnames


def make_random_firstnames(num):
    """Pull randomly (weighted by column weight) num rows with specified cols - firstname, sex from input file"""
    input_file = seed_data_folder/"first_names.csv"
    col_lst = ['firstname', 'sex']
    rows, weights = get_random_data_from_seed(input_file, col_lst, weight_col="weight")
    # random_firstnames = random.choices(rows, weights=weights, k=num)
    for _ in range(num):
        yield random.choices(rows, weights=weights, k=1)[0]
    # return random_firstnames


def make_random_email_domains(num):
    """Pull randomly (weighted by column weight) num rows with specified cols - domain from input file"""
    input_file = seed_data_folder/"first_names.csv"
    col_lst = ['domain']
    rows, weights = get_random_data_from_seed(input_file, col_lst, weight_col="weight")
    # random_email_domains = random.choices(rows, weights=weights, k=num)
    for _ in range(num):
        yield random.choices(rows, weights=weights, k=1)[0]
    # return random_email_domains

def random_string(char_lst, n):
    return ''.join(random.choices(char_lst, k=n))

def make_phone_numbers(num):
    for _ in range(num):
        yield f"{random.randomrange(100, 999)}-{random.randrange(1000,9999)}"

def make_random_surnames_gen(num):
    """Pull randomly (weighted by column weight) num rows with specified cols - surname  from input file"""
    input_file = seed_data_folder/"surnames.csv"
    col_lst = ['surname']
    rows, weights = get_random_data_from_seed(input_file, col_lst, weight_col="weight")
    for _ in range(num):
        yield random.choices(rows, weights=weights, k=1)[0]
   
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s",)
 