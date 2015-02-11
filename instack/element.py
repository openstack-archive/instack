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


import os
import string


class Element(object):
    """A diskimage-builder element."""

    def __init__(self, directory):
        """Element initialization.

        :param directory: The directory that defines the element.
        :type directory str.
        """
        if not os.access(directory, os.R_OK):
            raise Exception

        self.directory = directory
        self.hooks = {}
        self.load_hooks()

    def load_hooks(self):
        for f in os.listdir(self.directory):
            if not os.path.isdir(os.path.join(self.directory, f)):
                continue
            if not f.endswith('.d'):
                continue

            hook = f[:-2]
            hook_path = os.path.abspath(os.path.join(self.directory, f))

            for script in os.listdir(hook_path):
                if script[0:1] not in string.digits:
                    continue
                self.hooks.setdefault(
                    hook, []).append(os.path.join(hook_path, script))

    def get_hook(self, hook):
        return self.hooks.get(hook, [])
