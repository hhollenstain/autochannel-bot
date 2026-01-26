import argparse
import logging
import os

LOG = logging.getLogger(__name__)

def parse_arguments():
    """parsing arguments.

    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--debug', help='enable debug', action='store_true')

    return parser.parse_args()


def str2bool(v):
  return v.lower() in ("yes", "true", "y", "1")