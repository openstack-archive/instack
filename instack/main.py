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
from __future__ import print_function

import argparse
import errno
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import traceback

from instack import runner


LOG = logging.getLogger()


def load_args(argv):
    parser = argparse.ArgumentParser(
        description="Execute diskimage-builder elements on the current "
                    "system.")
    parser.add_argument(
        '-e', '--element', nargs='*',
        help="element(s) to execute")
    parser.add_argument(
        '-p', '--element-path', nargs='+',
        help=("element path(s) to search for elements (ELEMENTS_PATH "
              "environment variable will take precedence if defined)"))
    parser.add_argument(
        '-k', '--hook', nargs='*',
        help=("hook(s) to execute for each element"))
    parser.add_argument(
        '-b', '--blacklist', nargs='*',
        help=("script names, that if found, will be blacklisted and not run"))
    parser.add_argument(
        '-x', '--exclude-element', nargs='*',
        help=("element names that will be excluded from running even if "
              "they are listed as dependencies"))
    parser.add_argument(
        '-j', '--json-file',
        help=("read runtime configuration from json file"))
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
    parser.add_argument(
        '-l', '--logfile', action='store',
        default=os.path.join(os.path.expanduser('~'), '.instack/instack.log'),
        help=("Logfile to log all actions"))

    args = parser.parse_args(argv)

    if args.json_file and (args.element or args.hook or args.exclude_element):
        print("--json-file not compatible with --element, --hook,")
        print("--exclude-element, or --blacklist")
        sys.exit(1)

    return args


def set_environment(tmp_dir):
    """Set environment variables that diskimage-builder elements expect."""

    os.environ['TMP_MOUNT_PATH'] = os.path.join(tmp_dir, 'mnt')
    os.symlink('/', os.environ['TMP_MOUNT_PATH'])
    os.environ['DIB_OFFLINE'] = ''
    os.environ['DIB_INIT_SYSTEM'] = 'systemd'
    os.environ['DIB_IMAGE_CACHE'] = (
        '%s/.cache/image-create' % os.environ['HOME'])
    os.environ['IMAGE_NAME'] = 'instack'
    os.environ['PATH'] = "%s:/usr/local/bin" % os.environ['PATH']
    os.environ.setdefault('DIB_DEFAULT_INSTALLTYPE', 'package')

    if os.path.exists('/usr/share/diskimage-builder/lib'):
        os.environ['_LIB'] = '/usr/share/diskimage-builder/lib'
    elif os.path.exists('diskimage-builder/lib'):
        os.environ['_LIB'] = 'diskimage-builder/lib'
    else:
        raise Exception("Can't detect diskimage-builder lib directory.")

    os.environ['TARGET_ROOT'] = '/'
    if platform.processor() == 'x86_64':
        os.environ['ARCH'] = 'amd64'
    else:
        os.environ['ARCH'] = 'i386'

    os.environ['DIB_ENV'] = (
        subprocess.check_output(['export', '|', 'grep', '\' DIB_.*=\''],
                                shell=True))

    os.environ['DIB_ARGS'] = str(sys.argv)


def cleanup(tmp_dir):
    shutil.rmtree(tmp_dir)


def main(argv=sys.argv):
    args = load_args(argv[1:])

    tmp_dir = tempfile.mkdtemp(prefix='instack.')
    try:
        os.makedirs(os.path.dirname(args.logfile))
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    formatter = logging.Formatter("%(levelname)s: %(asctime)s -- %(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    LOG.setLevel(logging.DEBUG)
    LOG.addHandler(stream_handler)
    file_handler = logging.FileHandler(args.logfile)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    LOG.addHandler(file_handler)

    LOG.info("Starting run of instack")

    set_environment(tmp_dir)

    try:
        if args.json_file:
            LOG.info("Using json file: %s" % args.json_file)
            json_list = json.loads(open(args.json_file).read())
            if not isinstance(json_list, list):
                raise Exception("json file should be a list structure")

            for run in json_list:
                if "name" in run:
                    LOG.info("Running %s" % run["name"])
                em = runner.ElementRunner(
                    run['element'], run['hook'], args.element_path,
                    run.get('blacklist', []), run.get('exclude-element', []),
                    args.dry_run, args.interactive, args.no_cleanup)
                em.run()
        else:
            em = runner.ElementRunner(
                args.element, args.hook, args.element_path,
                args.blacklist, args.exclude_element,
                args.dry_run, args.interactive,
                args.no_cleanup)
            em.run()

    except Exception as e:
        LOG.error(e.message)
        LOG.error(traceback.print_tb(sys.exc_info()[2]))
        sys.exit(1)
    finally:
        cleanup(tmp_dir)

    LOG.info("Ending run of instack.")

if __name__ == '__main__':
    main()
