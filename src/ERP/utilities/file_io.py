import logging
import  csv

logger = logging.getLogger(__name__)

def create_csv(dict_gen, path_file_out, n):
    rows = dict_gen(n) # A list dictionary
    header = rows[0].keys()
    with open(path_file_out, 'w', newline='', encoding='utf-8') as write_obj:
        csv_writer = csv.DictWriter(write_obj, fieldnames=header)
        csv_writer.writeheader()
        csv_writer.writerows(rows)
        logger.info(f'{path_file_out}  {n} rows written')
