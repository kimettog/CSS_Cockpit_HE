# !/usr/bin/env python2.7

import os, sys, time, json, re, shutil, logging
from collections import OrderedDict
#from utils.reports import ResultSummary
#from cases import CONF
from utils.helpers import results_logs


log = logging.getLogger("sherry")


def generate_final_results(results_logs):
    try:
        log_path = results_logs.current_log_path
        test_build = results_logs.test_build
        if test_build not in log_path:
            return
        final_path = os.path.join(
            log_path.split(test_build)[0], test_build)
        report = ResultSummary(final_path, test_build)
        report.run()
    except Exception as e:
        log.error(e)


def main():
    if sys.argv[1] == '-h' or sys.argv[1] == '--help':
        str = """Main function entry.
    Usage:
        python run.py [argv]

    Options:
        h,help                                          Menu
        
        v41_he_standard_deploy                             Test v41_he_standard_deploy
    Example:
        python run.py v41_he_standard_deploy
    """
        print str
    else:
        tier = sys.argv[1]
        
        from cases import scen
        version = tier.split('_')[0]
        if version.startswith('v41'):
            import cases.v41 as ver_cases
        else:
            
            raise Exception("Please pick a valid scenario use -h to see the list")
            

        results_logs.test_build = CONF.get('common').get('test_build')

        from cases import scen
        
        cases_file = [c for c in getattr(scen, sys.argv[1])["CASES"]]
        
        for cf in cases_file:
             
            case = cf.split('/')[2].split('.')[0]
            
            results_logs.logger_name = 'check.log'
            
            results_logs.get_actual_logger(case)
            getattr(ver_cases, case).runtest()
            
        generate_final_results(results_logs)
        print "Debug :: generate_final_results "

if __name__ == '__main__':
    main()
