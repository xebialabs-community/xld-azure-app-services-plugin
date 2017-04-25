#
# Copyright 2017 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import unittest
import time

from itests import ResourceGroupCi

from azure_app_services.client import AzureClient

from azure_app_services import define_resource_group, remove_resource_group


class ResourceGroupTest(unittest.TestCase):

    def setUp(self):
        self.resource_group_ci = ResourceGroupCi()
        self.expected_name = "xld_azure_app_service_plugin_test_rg"
        self.resource_group_ci.resourceName = self.expected_name
        self.client = AzureClient.new_instance(self.resource_group_ci.subscription)

    def test_create_and_destroy_resource_group(self):
        self.assertFalse(self.client.resource_group_exists(self.expected_name))
        define_resource_group.create_or_update(self.resource_group_ci)
        self.assertTrue(self.client.resource_group_exists(self.expected_name))
        remove_resource_group.destroy(self.resource_group_ci)
        # Azure does not clean up right away, so not validating destroy.
        # time.sleep(10)
        # self.assertFalse(self.client.resource_group_exists(self.expected_name))




