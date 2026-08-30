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
    random_cities = random.choices(rows,  weights=weights, k=num)
    return random_cities

def make_random_streets(num):
    """Pull randomly (weighted by column weight) num rows with specified cols - street_name  from input file"""
    input_file = seed_data_folder/"street_names.csv"
    col_lst = ['street_name']
    rows, weights = get_random_data_from_seed(input_file, col_lst, weight_col="weight")
    random_streets = random.choices(rows,  weights=weights, k=num)
    return random_streets

def make_random_surnames(num):
    """Pull randomly (weighted by column weight) num rows with specified cols - surname  from input file"""
    input_file = seed_data_folder/"surnames.csv"
    col_lst = ['surname']
    rows, weights = get_random_data_from_seed(input_file, col_lst, weight_col="weight")
    random_surnames = random.choices(rows, weights=weights, k=num)
    return random_surnames


def make_random_firstnames(num):
    """Pull randomly (weighted by column weight) num rows with specified cols - firstname, sex from input file"""
    input_file = seed_data_folder/"first_names.csv"
    col_lst = ['firstname', 'sex']
    rows, weights = get_random_data_from_seed(input_file, col_lst, weight_col="weight")
    random_firstnames = random.choices(rows, weights=weights, k=num)
    return random_firstnames


def make_random_email_domains(num):
    """Pull randomly (weighted by column weight) num rows with specified cols - domain from input file"""
    input_file = seed_data_folder/"first_names.csv"
    col_lst = ['domain']
    rows, weights = get_random_data_from_seed(input_file, col_lst, weight_col="weight")
    random_email_domains = random.choices(rows, weights=weights, k=num)
    return random_email_domains

def random_string(char_lst, n):
    return ''.join(random.choices(char_lst, k=n))

# generate random customer id, with length=6, first 3 uppercase letters, followed by 3 digits
def customer_id(n):
    return random_string(string.ascii_uppercase, n) + random_string(string.digits, n)

# generate given number of customer ids
def make_customer_ids(n):
    count = 0
    customer_ids_set = set()
    while count < n:
        new_customer_id = customer_id(3)
        if new_customer_id in customer_ids_set:
            continue
        else:
            customer_ids_set.add(new_customer_id)
            count += 1      
    return [{'customer_id':customer_id}  for customer_id in customer_ids_set]

def get_business_types():
    return [1,2] # todo: get from postgres

def make_customer_names(n):

    """ Columns need to be generated in table customer_name for company_code US001:
    company_code char(5) check (company_code ~ '[A-Z]{2}[0-9]{3}' ) not null,
	customer_id char(6) primary key check (customer_id ~ '[A-Z]{3}[0-9]{3}' ),
    business_type_id integer not null,
	customer_name varchar(250),
    currency_id integer not null
    """
    company_code = 'US001'
    currency_id = 1
    business_type_lst = get_business_types()
    cust_ids = make_customer_ids(n)
    first_names = make_random_firstnames(n)
    surnames = make_random_surnames(n)
    ret = [{'company_code':company_code
             , 'customer_id':cust_ids[j]['customer_id']
             , 'business_type_id':(random.choices(business_type_lst, weights=[30,70], k=1))[0]
             , 'customer_name':(surnames[j]['surname'] + ',' + first_names[j]['firstname'])
             , 'currency_id':currency_id
             } for j in range(n)]
    return ret
    
def create_csv(dict_gen, path_file_out, n):
    rows = dict_gen(n) # A list dictionary
    header = rows[0].keys()
    with open(path_file_out, 'w', newline='', encoding='utf-8') as write_obj:
        csv_writer = csv.DictWriter(write_obj, fieldnames=header)
        csv_writer.writeheader()
        csv_writer.writerows(rows)
        logger.info(f'{path_file_out}  {n} rows written')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s",)
 