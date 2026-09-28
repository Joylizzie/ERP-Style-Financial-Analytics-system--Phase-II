import os
import logging
import random
import datetime
import csv
import itertools

random.seed(5)
logger = logging.getLogger(__name__)
# Save the period for the bash script

# without random.seed(5),if rerun the below code, the results of pre_sales_orders_items will be different because of random values were chosen.
# fetch existing sales_order_ids and product_ids in database where the company_code is 'US001'

# get connection via psycopg2
# def _get_conn(pw, user_str):
#    """use .bashrc to store postgres variables"""
#     conn = psycopg2.connect(host="localhost",
#                             database = db,
#                             user= user_str,
#                             password=pw)
#     conn.autocommit = False
#     return conn

# get connection via psycopg2
def _get_conn(user_str):
    """use .pgpass to store postgres variables"""
    conn = psycopg2.connect(host="localhost",
                            database = db,
                            user= user_str
                            )
    conn.autocommit = False
    return conn

# get sales order ids placed by individuals
def get_so_ids(conn, start_date, end_date):

    sql_so_i = """ select so.sales_order_id, cn.customer_id,cn.business_type_id from sales_orders as so
            inner join customer_names as cn
            on so.customer_id = cn.customer_id
            where cn.business_type_id = 2 
                  and  cn.company_code='US001' 
			      and so.s_order_date between %(start_date)s and %(end_date)s;             
         """
                 
    with conn.cursor() as curs:
        curs.execute("set search_path to ocean_stream;")
        curs.execute(sql_so_i,{'start_date':start_date, 'end_date':end_date})  #cursor closed after the execute action
        (sales_order_id_i) = curs.fetchall()
       
    conn.commit()
    print(len(sales_order_id_i)) #2588
    return sales_order_id_i


def get_product_ids(conn):

    sql_pi = """ select product_id, product_unit_price from products where company_code='US001' 
             """
    with  conn.cursor() as curs:
        curs.execute("set search_path to ocean_stream;")
        curs.execute(sql_pi)  #cursor closed after the execute action
        products = curs.fetchall()
    conn.commit() 

    #print(dict(products))
    return products
    
def weight_pro():

    pro_ids_lst = [3,4,5]
    product_weights = [30,30,40] 
    num_items_to_ship = random.choice(list(range(1,len(pro_ids_lst)+1)))
    # get product_id without repeating
    set_pro_ids = set()
    while len(set_pro_ids) < num_items_to_ship:        
        products_to_ship = random.choices(pro_ids_lst, weights = product_weights)
        set_pro_ids.add(products_to_ship[0])
    #print(set_pro_ids)
    return set_pro_ids   

        

# generate item(s) for a single sales order where placed by business
def so_items_i(so_id_i):
    product_id_3_units=random.choices([1,2,3], weights=[0.8, 0.1,0.1], k=1)[0]
    product_id_5_units=random.choices([1,2,3,4,5],weights=[0.75,0.1,0.05,0.05,0.05],k=1)[0]
    units_sold_dict = {3:product_id_3_units, 5:product_id_5_units, 4:random.randrange(1, 100)}
    selling_prices = dict(get_product_ids(conn))
    shipped_lst = ['yes', 'no']
    shipped_lst_weights = [99.5,0.5] # assuming there are 2% of orders were not shipped
    weight_pro_res = weight_pro()   
    return [('US001', #company_code
              so_id_i,
              product_id,
              units_sold_dict[product_id],
              selling_prices[product_id], #unit_selling_price 
              1,# currency_id
              1, # tax
              random.choices(shipped_lst, weights=shipped_lst_weights)[0] #shipped?
                ) 
             for product_id in weight_pro_res]  
                       
# generate all sales orders with the items generated above
def generate_value_tuples(conn,start_date, end_date):
    so_ids = get_so_ids(conn, start_date, end_date)
    lol = (so_items_i(so_id_i[0]) for so_id_i in so_ids)

    return list(itertools.chain(*lol))
    
# generate values and save in csv file, then upload to db from psql which is quicker comparing to below way.
def _to_csv(conn, start_date, end_date):
    tups = generate_value_tuples(conn, start_date, end_date)
    # Save the period for the bash script
    ym = start_date.strftime("%Y_%m")
                                           
    with open(os.path.join('data/intermediate_csv', f'pre_sales_orders_items_i_{ym}.csv'), 'w') as write_obj:
        csv_writer = csv.writer(write_obj)
        csv_writer.writerow(['company_code','sales_order_id', 'product_id', 'units', 'unit_selling_price', 'currency_id', 'tax_code', 'shipped'])
        for tup in tups:
            csv_writer.writerow(tup)
    print('Done individual customer sales order writing')


if __name__ == '__main__':
    db = 'ocean_stream'
    # pw = os.environ['POSTGRES_PW']
    # user_str = os.environ['POSTGRES_USER']
    # conn = _get_conn(pw, user_str)
    user_str = 'ocean_user'
    conn = _get_conn(user_str)
    start_date=datetime.date(2021,3,1)
    end_date= datetime.date(2021,7,31)
    #get_so_ids(conn, start_date, end_date)
    #get_product_ids(conn)
    #weight_pro()
    generate_value_tuples(conn,start_date, end_date)
    _to_csv(conn,start_date, end_date)
 
