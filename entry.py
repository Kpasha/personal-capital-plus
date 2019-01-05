import os
import json
import numpy as np
import pandas as pd
from os import path
import matplotlib.pyplot as plt
from argparse import (
    ArgumentParser,
    ArgumentDefaultsHelpFormatter
)
from collections import defaultdict, Counter

from requests import Session
from personalcapital.analyze import get_report
from personalcapital.etl import update_transactions


def report():
    report = get_report()
    session = Session()
    response = session.post("http://poorman.anthonyagnone.com/set_payload", json=report)
    print(json.dumps(report, indent=4))


def main(action):
    if action == 'update':
        update_transactions()
    elif action == 'report':
        report()
    else:
        raise ValueError("Unsupported action '{}'".format(action))


def get_clargs():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(dest="action", choices=['report', 'update'], help="Action to perform.")
    return parser.parse_args()


if __name__ == '__main__':
    args = get_clargs()
    main(args.action)
