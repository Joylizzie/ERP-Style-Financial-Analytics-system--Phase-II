import logging
import  csv

logger = logging.getLogger(__name__)

def create_csv(row_dict_gen_func, path_file_out, *args):
    """
    Executes a generator function and writes its outputs to a CSV file.
     *args captures whatever value you pass (the integer n OR the input file path)
    and passes it directly down to the generator function.
    """

    # Simply forward the argument (n or file path) directly to the generator
    gen = row_dict_gen_func(*args)
    
    try:
        # Extract the first row immediately to get the header keys
        first_row = next(gen)
        header = first_row.keys()
    except StopIteration:
        logger.warning(f"No records found to write for {path_file_out}")
        return
    
    with open(path_file_out, 'w', newline='', encoding='utf-8') as write_obj:
        csv_writer = csv.DictWriter(write_obj, fieldnames=header)
        csv_writer.writeheader()
        csv_writer.writerow(first_row)
        csv_writer.writerows(gen)
        logger.info(f'{path_file_out} written')

def read_csv_row_generator(input_path_file_name):
    with open(input_path_file_name, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)  # Yields each row as a dictionary
        for row in reader:
            yield row