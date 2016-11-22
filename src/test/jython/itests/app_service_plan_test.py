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





