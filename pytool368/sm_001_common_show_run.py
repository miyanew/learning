#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json
import os
import sys
import traceback
from datetime import datetime as dt

_current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(_current_dir, "./lib"))

from sm_001_common_show_configure_log import build_logger_app, logger_common

# from sm 001 common_show_evaluate_health_csdb import evaluate_health_csdb
# from sm 001 common_show_evaluate_health_csdbent import evaluate_health_csdbent
# from sm_001_common_show_evaluate_health_smf import evaluate_health_smf
# from sm 001 common_show_evaluate_health_smfent import evaluate_health_smfent
# from sm 001_common_show_evaluate_health_upf import evaluate_health_upf
# from sm 001_common_show_evaluate_health_upfent import evaluate_health_upfent
# from sm_001_common_show_execute_healthcheck_command import execute_commands

_config_dir = os.path.join(_current_dir, "config")


def main(options):
    logger_common.info("This is a normal log from run")
    logger_common.error("This is an error log from run")

    connect_props = select_connect_props(hostnames)
    print(connect_props)

    # for ret in results:
    #     cmd = [hc["command"] for hc in hcs if hc["id"] == ret["hc_id"]][0]
    #     ok_ng = "OK" if ret["is_healty"] else "NG"
    #     msg = f"result:{ok_ng} command:{cmd}"
    #     print(f"hc_id:{ret['hc_id']} result:{ok_ng} command:{cmd}")
    #     logger.info(msg)

    #     if ret["is healty"] is False:
    #         logger.info(ret["content"])


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
