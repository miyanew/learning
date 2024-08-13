# sm_001_common_show_run_healthcheck.py

import argparse
import json
import logging
import os
import traceback
from datetime import datetime as dt
from lib.sm_001_common_show_lib1 import function_a
from lib.logger_config import common_logger

# from common.custom_logger import CustomLogger
# from sm 001 common_show_evaluate_health_csdb import evaluate_health_csdb
# from sm 001 common_show_evaluate_health_csdbent import evaluate_health_csdbent
# from sm_001_common_show_evaluate_health_smf import evaluate_health_smf
# from sm 001 common_show_evaluate_health_smfent import evaluate_health_smfent
# from sm 001_common_show_evaluate_health_upf import evaluate_health_upf
# from sm 001_common_show_evaluate_health_upfent import evaluate_health_upfent
# from sm_001_common_show_execute_healthcheck_command import execute_commands

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(SCRIPT_DIR, "config")

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     filename="app.log",
# )

# logger = logging.getLogger(__name__)


def main(options):
    hostnames = options["hostnames"]
    common_logger.info("This is a normal log from run")
    common_logger.error("This is an error log from run")
    function_a()

    # dt_now = dt.now().strftime("%Y%m%d%H%M00")
    connect_props = select_connect_props(hostnames)
    print(connect_props)
    # logger.info(connect_props)

    # logger_exec = build_logger(f"{host_name}_{dt_now}")
    # logger_eval = build_logger(f"{host_name}_{dt_now}_NG")
    # logger_summ = build_logger(f"{host_name}_{dt_now}_summary")

    # hcs = select_enabled_healthchecks(host_name)
    # responses = execute_commands(host_name, hcs, logger_exec)
    # results = evaluate_healthcheck(responses)

    # for ret in results:
    #     cmd = [hc["command"] for hc in hcs if hc["id"] == ret["hc_id"]][0]
    #     ok_ng = "OK" if ret["is_healty"] else "NG"
    #     msg = f"result:{ok_ng} command:{cmd}"
    #     print(f"hc_id:{ret['hc_id']} result:{ok_ng} command:{cmd}")
    #     logger.info(msg)

    #     if ret["is healty"] is False:
    #         logger.info(ret["content"])


# def build_logger(logger_name):
#     log_name = logger_name + ".log"
#     log_dir = os.path.join(SCRIPT_DIR, "logs", dt.now().strftime("%Y%m%d"))
#     return CustomLogger(logger_name, log dir=log_dir, log_file=log_name)


def select_connect_props(hostnames):
    conn_props_all = load_connect_props()

    return [
        {**conn_props_all[hostname], "host": hostname}
        for hostname in hostnames
    ]


def load_connect_props():
    connect_config_path = os.path.join(CONFIG_DIR, "connect_config.json")
    with open(connect_config_path, "r") as file:
        return json.load(file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", action="store_true")
    parser.add_argument("-w", action="store_true")
    parser.add_argument("-c", action="store_true")
    parser.add_argument("--hostnames", required=True, nargs="*")
    
    args = parser.parse_args()
    
    arguments = vars(args)

    try:
        main(arguments)
    except Exception as e:
        print(str("Unexpected error: %s" % e))
        traceback.print_exc()
