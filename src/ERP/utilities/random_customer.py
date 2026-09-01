import random
import string
# from ERP.db.db_utilities import connection_pool, copy_file_to_db
from ERP.utilities.random_gen import random_string, make_random_firstnames, \
       make_random_surnames, make_random_cities, make_random_email_domains, make_random_streets

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


"""
# def make_customer_addresses(data_file):
#     df = pd.read_csv('data/customer_names.csv', usecols=['customer_id'])
#     n = len(df['customer_id'])
#     print(n)
#     customer_ids_lst = df['customer_id'].values.tolist()
#     cities_list = make_random_data.make_random_cities(path = 'data/wash_cities.csv', num = n)
#     customer_surnames = make_random_data.make_random_surnames(path = 'data/surnames.csv', num = n)
#     customer_first_names = make_random_data.make_random_first_names(path = 'data/first_names.csv', num = n)
#     phone_nums = make_random_data.make_phone_numbers(num = n)
#     street_addresses = make_random_data.make_street_address(path = 'data/street_names.csv', num = n)
#     emails = make_random_data.make_random_email_domains(path = 'data/emails.csv', num = n)
#     # return a list of tuples for customer_addresses table
#     return [('US001',# company_code
            customer_ids_lst[k], # customer_id,
            '{n} {s}'.format(n = random.randrange(1,100), s = street_addresses[k]),# address_line1
            cities_list[k][0],# city
            'WA',# state
            'USA', # country
            cities_list[k][1], # postcode
            '{z}-{n}'.format(z = cities_list[k][2], n = phone_nums[k]),# phone_number
            '{l}@{d}'.format(
                            f = customer_first_names[k][0].lower()[0:5], 
                            l = customer_surnames[k].lower()[0:7],
                            d = emails[k]) # email_address
              ) for k in range(n)
             ]
             """