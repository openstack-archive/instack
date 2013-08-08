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


from distutils import dir_util
import logging
import os
import tempfile

from dib_elements.element import Element
from dib_elements.util import call

from diskimage_builder.elements import expand_dependencies

class ElementManager(object):

    def __init__(self, elements, hooks, element_paths=None, dry_run=False):
        """
        :param elements: Element names to apply.
        :type elements: list.
        :param hooks: Hooks to run for each element.
        :type hooks: list.
        :param element_paths: File system paths to search for elements.
        :type element_paths: list of strings.
        :param dry_run: If True, do not actually run the hooks.
        :type dry_run: bool
        """
        self.elements = elements
        self.dry_run = dry_run
        self.hooks = hooks
        self.loaded_elements = {}

        # the environment variable should override anything passed in
        if os.environ.has_key('ELEMENTS_PATH'):
            self.element_paths = os.environ['ELEMENTS_PATH'].split(':')
        else:
            self.element_paths = element_paths

        if self.element_paths is None:        
            raise Exception

        logging.debug('manager initialized with elements path: %s' %
                      self.element_paths)

        self.load_elements()
        self.load_dependencies()
        self.copy_elements()

    def run(self):
        for hook in self.hooks:
            self.run_hook(hook)

    def load_elements(self):
        """Load all elements from self.element_paths.

        This populates self.loaded_elements.
        """
        for path in self.element_paths:
            self.process_path(path)

    def copy_elements(self):
        """Copy elements to apply to a temporary directory."""
        self.tmp_hook_dir = tempfile.mkdtemp()
        for element in self.elements:
            element_dir = self.loaded_elements[element].directory
            dir_util.copy_tree(element_dir, self.tmp_hook_dir)
        # elements expect this environment variable to be set
        os.environ['TMP_HOOKS_PATH'] = self.tmp_hook_dir

    def process_path(self, path):
        """Load elements from a given filesystem path.

        :param path: Filesystem path from which to load elements.
        :type path: str.
        """
        if not os.access(path, os.R_OK):
            raise Exception

        for element in os.listdir(path):
            if not os.path.isdir(os.path.join(path, element)):
                continue
            if self.loaded_elements.has_key(element):
                raise Exception
            self.loaded_elements[element] = Element(os.path.join(path, element))

    def load_dependencies(self):
        all_elements = expand_dependencies(
            self.elements, ':'.join(self.element_paths))
        self.elements = all_elements

    def run_hook(self, hook):
        scripts = []
        for element in self.loaded_elements:
            if element in self.elements:
                scripts += self.loaded_elements[element].get_hook(hook) 

        scripts = sorted(scripts, key=lambda script: os.path.basename(script))

        for script in scripts:
            if not self.dry_run:
                call(['sudo', '-E', '/bin/bash', script])
            else:
                logging.info("script to execute: %s" % script)
