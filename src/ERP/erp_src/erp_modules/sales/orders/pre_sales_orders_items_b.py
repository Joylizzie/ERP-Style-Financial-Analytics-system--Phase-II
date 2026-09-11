import os
import psycopg2
import random
import datetime
import csv
import itertools

random.seed(5)

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
def get_so_ids_b(conn, start_date, end_date):

    sql_so_b = """ select so.sales_order_id from sales_orders as so
            inner join customer_names as cn
            on so.customer_id = cn.customer_id
            where cn.business_type_id = 1 
                  and  cn.company_code='US001' 
			      and so.s_order_date between %(start_date)s and %(end_date)s;             
         """                  
    with conn.cursor() as curs:
        curs.execute("set search_path to ocean_stream;")
        curs.execute(sql_so_b,{'start_date':start_date, 'end_date':end_date})  #cursor closed after the execute action
        (sales_order_id_b) = curs.fetchall()        
    conn.commit()

    #print(sales_order_id_b) 
    #print(len(sales_order_id_b)) 
    return sales_order_id_b


def get_product_ids(conn):

    sql_pi = """ select product_id, product_unit_price from products where company_code='US001' 
             """
    with conn.cursor() as curs:
        curs.execute("set search_path to ocean_stream;")
        curs.execute(sql_pi)  #cursor closed after the execute action
        products = curs.fetchall()
    conn.commit() 

    #print(dict(products))
    return products
    
          
# generate item(s) for a single sales order where placed by business
def so_items_b(so_id):

    units_sold_dict = {1:1, 2:1, 3:random.randrange(1, 20),4:random.randrange(1, 30),5:random.randrange(1, 40), 6:random.randrange(10, 300)}
    
    selling_prices = dict(get_product_ids(conn))
    shipped_lst = ['yes', 'no']
    shipped_lst_weights = [99,1] # assuming there are 1% of orders were not shipped
    
    #done = False
    pro_mix_lst = [(2,), (3,), (4,), (5,),(6,), (1, 2),(2, 4), (2, 5), (2, 6),(3, 4),(3, 5), (3, 6), (4, 5),(4, 6), (5, 6),(1, 2, 4), (1, 2, 5), (1, 2, 6),(3, 4, 5),(3, 4, 6), (3, 5, 6),(1, 2, 4, 5), (1, 2, 4, 6), (1, 2, 5, 6),(2, 4, 5, 6), (3, 4, 5, 6),(1, 2, 4, 5, 6)]
    
    pro_mix_lst_weights = [0.01,0.1,0.1,0.1,0.1,0.01,0.01,0.01,0.01,0.09,0.1,0.1,0.01,0.02,0.01,0.01,0.01,0.01,0.03,0.06,0.01,0.01,0.01,0.01,0.01,0.04,0.01]
    #print(len(pro_mix_lst_weights))
    #print(sum(pro_mix_lst_weights))
    product_ids_tup = random.choices(pro_mix_lst, weights=pro_mix_lst_weights, k=1)
    product_ids = list(*product_ids_tup)

    return [('US001', #company_code
              so_id,
              product_id,
              units_sold_dict[product_id],
              selling_prices[product_id], #unit_selling_price 
              1,# currency_id
              1, # tax
              random.choices(shipped_lst, weights=shipped_lst_weights)[0] #shipped?
                ) 
             for product_id in product_ids] 
   
# generate all sales orders with the items generated above
def generate_value_tuples(conn,start_date, end_date):
    so_ids = get_so_ids_b(conn, start_date, end_date)
    lol = (so_items_b(so_id_b[0]) for so_id_b in so_ids)

    return list(itertools.chain(*lol))
    
# generate values and save in csv file, then upload to db from psql which is quicker comparing to below way.
def _to_csv(conn, start_date, end_date):
    tups = generate_value_tuples(conn, start_date, end_date)
    #print(tups)
    ym = start_date.strftime("%Y_%m")
    
    with open(os.path.join('data/intermediate_csv', f'pre_sales_orders_items_b_{ym}.csv'), 'w') as write_obj:
        csv_writer = csv.writer(write_obj)
        csv_writer.writerow(['company_code','sales_order_id', 'product_id', 'units', 'unit_selling_price', 'currency_id', 'tax_code', 'shipped'])
        for tup in tups:
            csv_writer.writerow(tup)
    # Save the period for the bash script
    with open(os.path.join('data', 'intermediate_csv', f'pre_sales_orders_items_b_{ym}.txt'), 'w') as f:
        f.write(ym)
    print('Done Business sales order writing')


if __name__ == '__main__':
    db = 'ocean_stream'
    # pw = os.environ['POSTGRES_PW']
    # user_str = os.environ['POSTGRES_USER']
    # conn = _get_conn(pw, user_str)
    user_str = 'ocean_user'
    conn = _get_conn(user_str)
    start_date=datetime.date(2021,3,1)
    end_date= datetime.date(2021,7,31)

    generate_value_tuples(conn,start_date, end_date)
    _to_csv(conn,start_date, end_date)
 
