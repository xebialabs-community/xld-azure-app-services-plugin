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




