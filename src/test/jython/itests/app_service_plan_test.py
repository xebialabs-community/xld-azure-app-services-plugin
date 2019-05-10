#
# Copyright 2019 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import unittest
import time

from azure_app_services.client import AzureClient
from itests import ResourceGroupCi, AppServicePlanCi
from azure_app_services import define_app_service_plan, remove_app_service_plan


class AppServicePlanTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.resource_group_ci = ResourceGroupCi()
        self.app_service_plan_ci = AppServicePlanCi()
        self.expected_name = self.app_service_plan_ci.servicePlanName
        self.app_service_plan_ci.container = self.resource_group_ci
        self.expected_rg = self.resource_group_ci.resourceName
        self.client = AzureClient.new_instance(self.resource_group_ci.subscription)
        self.client.create_resource_group(self.resource_group_ci.resourceName, self.resource_group_ci.resourceLocation)

    @classmethod
    def tearDownClass(self):
        self.client.destroy_resource_group(self.resource_group_ci.resourceName)

    def test_app_service_plan(self):
        self.assertFalse(self.client.app_service_plan_exists(self.expected_rg , self.expected_name))
        define_app_service_plan.create_or_update(self.app_service_plan_ci, self.resource_group_ci)
        self.assertTrue(self.client.app_service_plan_exists(self.expected_rg , self.expected_name))
        remove_app_service_plan.destroy(self.app_service_plan_ci, self.resource_group_ci)
        # Azure does not clean up right away
        time.sleep(10)
        self.assertFalse(self.client.app_service_plan_exists(self.expected_rg, self.expected_name))





