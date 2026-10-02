import os
import logging
import random
import datetime
import csv
import itertools
from ERP.db.db_utilities import run_sql
from ERP.erp_src.erp_modules.sales.orders.product_mix import ProductMix

logger = logging.getLogger(__name__)
random.seed(5)

# without random.seed(5),if rerun the below code, the results of pre_sales_orders_items will be different because of random values were chosen.
# fetch existing sales_order_ids and product_ids in database where the company_code is 'US001'

# get connection via psycopg2
# def _get_conn(user_str):
#     """use .pgpass to store postgres variables"""
#     conn = psycopg2.connect(host="localhost",
#                             database = db,
#                             user= user_str
#                             )
#     conn.autocommit = False
#     return conn

def get_so_ids_b(business_type_id, start_date, end_date):
    """ get sales order ids placed by business"""
    sql_so_b = """ select so.sales_order_id from sales_orders as so
            inner join customer_names as cn
            on so.customer_id = cn.customer_id
            where cn.business_type_id = %(business_type_id)s 
                  and  cn.company_code='US001' 
			      and so.s_order_date between %(start_date)s and %(end_date)s;             
         """                  
    params_dict = {'business_type_id':business_type_id,'start_date':start_date, 'end_date':end_date}
    sales_order_id = run_sql(sql_so_b, params_dict)

    logger.info(f'There are {len(sales_order_id)} generated') 
    return sales_order_id


def get_product_id_price():
    sql = """ select product_id, product_unit_price from products where company_code='US001' 
             """
    product_id_price = run_sql(sql)

    return product_id_price
    
          
def so_items_b(so_id, selling_prices_dict, pm_dict, pm_weight):
    """ '1' is business_type_id for business. generate item(s) for a single sales order which placed by business"""
    #TODO change to parameters 
    units_sold_dict = {1:1, 2:1, 3:random.randrange(1, 20),4:random.randrange(1, 30),5:random.randrange(1, 40), 6:random.randrange(10, 300)}
    
    shipped_lst = ['yes', 'no']
    shipped_lst_weights = [99,1] # assuming there are 1% of orders were not shipped

    (pm_ids_tup, pm_cum_weight_tup) = pm_weight

    # pro_mix_lst = [(2,), (3,), (4,), (5,),(6,), (1, 2),(2, 4), (2, 5), (2, 6),(3, 4),(3, 5), (3, 6), (4, 5),(4, 6), (5, 6),(1, 2, 4), (1, 2, 5), (1, 2, 6),(3, 4, 5),(3, 4, 6), (3, 5, 6),(1, 2, 4, 5), (1, 2, 4, 6), (1, 2, 5, 6),(2, 4, 5, 6), (3, 4, 5, 6),(1, 2, 4, 5, 6)]
    # pro_mix_lst_weights = [0.01,0.1,0.1,0.1,0.1,0.01,0.01,0.01,0.01,0.09,0.1,0.1,0.01,0.02,0.01,0.01,0.01,0.01,0.03,0.06,0.01,0.01,0.01,0.01,0.01,0.04,0.01]
    
    pm_id = random.choices(pm_ids_tup, cum_weights=pm_cum_weight_tup, k=1)
    product_ids = pm_dict[pm_id]

    return [('US001', #company_code
              so_id,
              product_id,
              units_sold_dict[product_id],
              selling_prices_dict[product_id], #unit_selling_price 
              1,# currency_id
              1, # tax
              random.choices(shipped_lst, weights=shipped_lst_weights)[0] #shipped?
                ) 
             for product_id in product_ids] 
   
# generate all sales orders with the items generated above
def sales_order_item_value_tuples_gen(business_type_id, start_date, end_date):

    pro_mix = ProductMix(business_type_id)
    pm_dict = pro_mix.get_product_mix_lst()
    pm_weight = tuple(zip(*(pro_mix.get_cum_weights())))
    selling_prices_dict = dict(get_product_id_price())
    so_ids = get_so_ids_b(business_type_id, start_date, end_date)
    lol = (so_items_b(so_id_b[0], selling_prices_dict, pm_dict, pm_weight) for so_id_b in so_ids)

    return list(itertools.chain(*lol))
    
# generate values and save in csv file, then upload to db from psql which is quicker comparing to below way.
def _to_csv(conn, start_date, end_date):
    tups = sales_order_item_value_tuples_gen(conn, start_date, end_date)
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
 
