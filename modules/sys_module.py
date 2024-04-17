# -*- coding: utf-8 -*-

"""
This module provides utility functions to working with argv, file and json.
Author: Andres Felipe Forero Correa
Date: 2023-06-30
"""

import os
import sys
import json


def check_filepath(*args):
    """Verify if each filepath exits"""
    for filepath in args:
        if not os.path.exists(filepath):
            print(f"ERROR: '{filepath}' filepath does not exist.")
            sys.exit(1)


def read_file(filepath):
    """Read data from file"""
    try:
        with open(filepath, encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"ERROR: {filepath} does not exist.")
        sys.exit(1)
    except PermissionError:
        print(f"ERROR: permission denied to access {filepath}.")
        sys.exit(1)


def check_len_sys_argv(sys_argv, len_required_argv):
    """Verify lenght of sys args"""
    if len(sys_argv) != len_required_argv:
        print(f"ERROR: there are {len(sys_argv)} sys args. \
              It is required {len_required_argv} sys args.")
        sys.exit(1)


def parse_json(json_string):
    """Parse JSON string to JSON object"""
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as json_decode_error:
        print(f"ERROR: {json_decode_error}")
        sys.exit(1)
