import logging
import argparse
from ERP import erp_main


logger = logging.getLogger(__name__)

def get_args(cmd_args=None):
    """Configure commandline: where to get source data -- query dw or existing csv files;
    where to save output files; Environment -- prod or statging; period:--start_time, end_time
    :return: namespace
    """
    commandline_parser = argparse.ArgumentParser(description='Data pipeline extraction and environment setup.')

    commandline_parser.add_argument('--env', choices = ['dev', 'preproduction', 'production'], default='dev', help='Deployment environment')
    # commandline_parser.add_argument('--format', choices = ['Parquet', 'csv'])
    commandline_parser.add_argument('--start_month', help='Period start month (YYYY-MM')
    commandline_parser.add_argument('--end_month', help='Period end month (YYYY-MM)')
    if cmd_args:
        return commandline_parser.parse_args(cmd_args)
    return commandline_parser.parse_args()


def main(cmd_args=None):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    args = get_args(cmd_args)
    logger.info(f'args are {args}')
    erp_main.main()


if __name__ == '__main__':
    main()
