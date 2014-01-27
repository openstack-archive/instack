# Copyright 2013, Red Hat Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import argparse
import logging
import os
import platform
import sys

from instack import runner


def load_args(argv):
    parser = argparse.ArgumentParser(
        description="Execute diskimage-builder elements on the current "
                    "system.")
    parser.add_argument(
        '-e', '--element', nargs='+',
        help="element(s) to execute")
    parser.add_argument(
        '-p', '--element-path', nargs='+',
        help=("element path(s) to search for elements (ELEMENTS_PATH "
              "environment variable will take precedence if defined)"))
    parser.add_argument(
        '-k', '--hook', nargs='+', required=True,
        help=("hook(s) to execute for each element"))
    parser.add_argument(
        '-b', '--blacklist', nargs='+',
        help=("script names, that if found, will be blacklisted and not run"))
    parser.add_argument(
        '-x', '--exclude-element', nargs='+',
        help=("element names that will be excluded from running even if "
              "they are listed as dependencies"))
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help=("Debugging output"))
    parser.add_argument(
        '-i', '--interactive', action='store_true',
        help=("If set, prompt to continue running after a failed script."))
    parser.add_argument(
        '--dry-run', action='store_true',
        help=("Dry run only, don't actually modify system, prints out "
              "what would have been run."))
    parser.add_argument(
        '--no-cleanup', action='store_true',
        help=("Do not cleanup tmp directories"))
    return parser.parse_args(argv)


def set_environment():
    """Set environment variables that diskimage-builder elements expect."""

    os.environ['TMP_MOUNT_PATH'] = '/'
    os.environ['DIB_OFFLINE'] = ''
    os.environ['DIB_INIT_SYSTEM'] = 'systemd'
    os.environ['PATH'] = "%s:/usr/local/bin" % os.environ['PATH']
    if platform.processor() == 'x86_64':
        os.environ['ARCH'] = 'amd64'
    else:
        os.environ['ARCH'] = 'i386'


def main(argv=sys.argv):
    args = load_args(argv[1:])
    set_environment()
    if args.debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(levelname)s:%(asctime)s:%(name)s:%(message)s")
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(levelname)s:%(asctime)s:%(name)s:%(message)s")
    em = runner.ElementRunner(args.element, args.hook, args.element_path,
                              args.blacklist, args.exclude_element,
                              args.dry_run, args.interactive, args.no_cleanup)
    em.run()


if __name__ == '__main__':
    main()
