#!/usr/bin/env python2.7
#
# Copyright @ 2018 Atlassian Pty Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# author: George Politis

import os
import sys
import time
import signal
import logging
import argparse
from selenium import webdriver

def parse_line(line):
    # TODO support FF and other browsers.
    options = webdriver.ChromeOptions()
    split = line.split()
    options.binary_location = split.pop(0)
    url = split.pop()

    for arg in split:
        options.add_argument(arg)

    return options.to_capabilities(), url

def signal_handler(signal, frame):
    global drivers
    for driver in drivers:
        try:
            driver.quit()
        except:
            logging.exception("Failed to quit a driver.")
    sys.exit(0)

def join(args):

    # start chrome
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    global drivers

    drivers = []
    for line in sys.stdin:
        desired_capabilities, url = parse_line(line)
        driver = webdriver.Remote(command_executor=args.command_executor,
                            desired_capabilities=desired_capabilities)
        drivers.append(driver)
        driver.get(url)

    while True:
        time.sleep(5)
        for driver in drivers:
            driver.execute_script("console.log('keepalive');")


def main():
    # parse the arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-level', dest="loglevel",
            default=os.environ.get('SELENIUM_LOG_LEVEL', None), type=str)
    parser.add_argument('-e', '--executor', dest="command_executor", type=str,
            default=os.environ.get('SELENIUM_EXECUTOR', None))

    args = parser.parse_args()

    # set the logging level from the cmd line parameters.
    if args.loglevel:
        logging.basicConfig(stream=sys.stderr, level=args.loglevel)

    if not args.command_executor: exit(parser.print_usage())

    join(args)

if __name__ == "__main__":
    main()
