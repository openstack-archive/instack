# Copyright 2013 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import os
import tempfile

import mock
import testtools

from instack import runner


class TestRunner(testtools.TestCase):

    def setUp(self):
        super(TestRunner, self).setUp()
        cwd = os.path.dirname(__file__)
        # dib_elements = os.path.join(cwd, '..', '..', 'elements')
        test_elements = os.path.join(cwd, 'elements')
        self.element_paths = [test_elements]

        self.patcher = mock.patch.object(runner.ElementRunner,
                                         'generate_environment')
        self.mock_env = self.patcher.start()
        self.runner = runner.ElementRunner(['dep2', 'echo', 'os'], [],
                                           self.element_paths)
        tmp_dir = tempfile.mkdtemp()
        self.runner.tmp_hook_dir = tmp_dir

    def tearDown(self):
        super(TestRunner, self).tearDown()
        self.patcher.stop()

    def test_cleanup(self):
        self.runner.cleanup()
        self.assertFalse(os.path.exists(self.runner.tmp_hook_dir))

    @mock.patch.object(runner.ElementRunner, 'process_path')
    def test_load_elements(self, mock_method):
        self.runner.load_elements()

        self.assertEqual(len(self.element_paths), mock_method.call_count)
        for idx in range(len(self.element_paths)):
            self.assertEqual(mock.call(self.element_paths[idx]),
                             mock_method.call_args_list[idx])

    def test_copy_elements(self):
        self.runner.copy_elements()

        self.assertTrue(
            os.path.exists(
                os.path.join(
                    self.runner.tmp_hook_dir, 'install.d', '50-echo')))
        self.assertTrue(
            os.path.exists(
                os.path.join(
                    self.runner.tmp_hook_dir, 'install.d', '50-dep2')))

    def test_load_dependencies(self):
        self.runner.copy_elements()
        self.runner.load_dependencies()

        self.assertEqual(4, len(self.runner.elements))
        self.assertIn('dep1', self.runner.elements)

    def test_process_exclude_elements(self):
        self.runner.exclude_elements = ['dep1']

        self.runner.copy_elements()
        self.runner.load_dependencies()
        self.assertEqual('dep1 dep2 echo os',
                         os.environ['IMAGE_ELEMENT'])
        self.runner.process_exclude_elements()

        self.assertEqual(3, len(self.runner.elements))
        self.assertNotIn('dep1', self.runner.elements)
        self.assertEqual('dep2 echo os',
                         os.environ['IMAGE_ELEMENT'])

    def test_process_path(self):
        cwd = os.path.dirname(__file__)
        test_elements = os.path.join(cwd, 'elements')
        self.runner.loaded_elements = {}
        self.runner.process_path(test_elements)

        self.assertEqual(7, len(self.runner.loaded_elements))
        self.assertIn('dep1', self.runner.loaded_elements)
        self.assertIn('dep2', self.runner.loaded_elements)
        self.assertIn('echo', self.runner.loaded_elements)
        self.assertIn('error', self.runner.loaded_elements)
        self.assertIn('output', self.runner.loaded_elements)
        self.assertIn('repo', self.runner.loaded_elements)

        self.assertRaises(Exception, self.runner.process_path,
                          '/tmp/non/existant/path')  # noqa

    @mock.patch('instack.runner.call',
                return_value=0)
    def test_run_hook(self, mock_call):
        self.runner.copy_elements()
        self.runner.load_dependencies()
        self.runner.process_exclude_elements()

        self.runner.run_hook('install')

        self.assertEqual(1, mock_call.call_count)
        self.assertEqual(
            [runner._DIB_RUN_PARTS,
             os.path.join(self.runner.tmp_hook_dir, 'install.d')],
            mock_call.call_args_list[0][0][0])

    @mock.patch('instack.runner.call',
                return_value=0)
    def test_blacklist(self, mock_call):
        self.runner.copy_elements()
        self.runner.load_dependencies()
        self.runner.process_exclude_elements()

        self.runner.blacklist = ['50-echo']
        self.runner.run_hook('install')

        self.assertNotIn(
            '50-echo',
            os.listdir(os.path.join(self.runner.tmp_hook_dir, 'install.d')))
