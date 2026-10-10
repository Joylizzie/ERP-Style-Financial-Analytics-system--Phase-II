import logging
import ERP.db.db_utilities as dbutil
import ERP.db.ocean_pool as ocean_pool
import ERP.erp_src.erp_modules.reports.transaction_list as tran_lst
logging = logging.getLogger(__name__)


class TranLst:
    def __init__(self, sql, params, outpath, outfile):
        self.sql = sql
        self.param = params
        self.pathfile = self.path/self.outfile
        
    def trans_lst(sql, *args, outfile=None):
        pool = ocean_pool()
        if outfile:
            dbutil.copy_from_db_file(outfile,sql, *args, pool)

