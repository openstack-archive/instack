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


import logging
import os

from dib_elements.element import Element
from dib_elements.util import call

from diskimage_builder.elements import expand_dependencies

class ElementManager(object):

    def __init__(self, elements, element_paths=None):
        self.elements = elements

        if os.environ.has_key('ELEMENTS_PATH'):
            self.element_paths = os.environ['ELEMENTS_PATH'].split(':')
        else:
            self.element_paths = element_paths

        if self.element_paths is None:        
            raise Exception

        logging.debug('manager initialized with elements path: %s' %
                      self.element_paths)

        self.loaded_elements = {}
        self.load_elements()
        self.load_dependencies()

    def load_elements(self):
        for path in self.element_paths:
            self.process_path(path)

    def process_path(self, path):
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
            call(['sudo', '-i', '/bin/bash', script])
