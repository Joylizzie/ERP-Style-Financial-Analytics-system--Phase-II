import random
from pathlib import Path
import string
from ERP.utilities.file_io import read_csv_row_generator
from ERP.utilities.random_gen_generator import random_string, make_random_firstnames, \
       make_random_surnames, make_random_cities, make_random_email_domains, make_random_streets, make_phone_numbers

project_root_folder = Path().resolve()
seed_data_folder = project_root_folder/"src"/"ERP"/"data"/"master_data"/"seed_data"
made_data_fr_seed_random_folder = project_root_folder/"src"/"ERP"/"data"/"master_data"/"made_data_fr_seed_random"

# generate random customer id, with length=6, first 3 uppercase letters, followed by 3 digits
def make_customer_id(n):
    return random_string(string.ascii_uppercase, n) + random_string(string.digits, n)

# generate given number of customer ids
def make_customer_ids(n):
    count = 0
    customer_ids_set = set()
    while count < n:
        customer_id = make_customer_id(3)
        if customer_id in customer_ids_set:
            continue
        else:
            customer_ids_set.add(customer_id)
            count += 1      
    # return [{'customer_id':customer_id}  for customer_id in customer_ids_set]
        yield customer_id

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
    for _ in range(n):
        ret = {'company_code':company_code
                , 'customer_id': next(cust_ids)
                , 'business_type_id': (random.choices(business_type_lst, weights=[30,70], k=1))[0]
                , 'firstname': next(first_names)['firstname']
                , 'surname': next(surnames)['surname']
                , 'currency_id':currency_id
                } 
        yield ret


def make_customer_addresses(input_path_file_name):
    """Add address, phone, email to db existing customers from seed data;
    Calculates file_rows automatically from the input file."""
    with open(input_path_file_name, 'r') as file:
        file_rows = sum(1 for line in file) - 1 # subtract 1 for header row. Find how many customer_ids without address

    city_gen = make_random_cities(file_rows)
    phone_num_gen = make_phone_numbers(num=file_rows)
    street_address_gen = make_random_streets(file_rows)
    emails_domain_gen = make_random_email_domains(file_rows)
    customer_name_file_gen = read_csv_row_generator(input_path_file_name)

    for _ in range(file_rows):
        row = next(customer_name_file_gen) # row a dictionary
        customer_id, firstname, surname = row['customer_id'], row['firstname'], row['surname']
        row = next(city_gen)
        city, zip_code, area_code = row['city'], row['zip_code'], row['area_code']
        phone_7 = next(phone_num_gen)
        street_name = next(street_address_gen)['street_name']
        email_domain = next(emails_domain_gen)['domain']
        street_num = random.randrange(1, 999)
        phone_number = f"{area_code}-{phone_7}"
        email_address = f"{firstname[0:5]}_{surname[0:7]}@{email_domain}".lower()

        ret = {'company_code': 'US001'
               , 'customer_id': customer_id
               , 'address_line1' : f"{street_num} {street_name}"
               , 'city': city
               , 'state': 'WA'# state
               , 'country': 'USA' 
               , 'postcode': zip_code
               , 'phone_number' : phone_number
               , 'email_address': email_address
            } 
        yield ret