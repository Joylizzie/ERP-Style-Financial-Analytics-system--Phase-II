import logging
import  csv
import itertools

logger = logging.getLogger(__name__)

def create_csv(row_dict_gen, path_file_out, n=None):
    rows, peek_rows = itertools.tee(row_dict_gen(n) if n else row_dict_gen)
    header = next(peek_rows).keys()
    with open(path_file_out, 'w', newline='', encoding='utf-8') as write_obj:
        csv_writer = csv.DictWriter(write_obj, fieldnames=header)
        csv_writer.writeheader()
        csv_writer.writerows(rows)
        logger.info(f'{path_file_out}  {n} rows written')

def read_csv_row_generator(input_path_file_name):
    with open(input_path_file_name, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)  # Yields each row as a dictionary
        for row in reader:
            yield row