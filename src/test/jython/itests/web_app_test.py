import unittest
import time
from com.microsoft.azure.management.websites.models import DatabaseServerType

from azure_app_services.client import AzureClient
from itests import ResourceGroupCi, AppServicePlanCi, WebAppCi
from azure_app_services import define_app_service_plan, define_web_app, remove_web_app, upload_web_app_artifact

from java.lang import Thread
from java.io import File

class WebAppTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        rg = ResourceGroupCi()
        self.resource_group = rg.resourceName
        self.client = AzureClient.new_instance(rg.subscription)
        plan = AppServicePlanCi()
        plan.container = rg
        self.web_app_ci = WebAppCi()
        self.web_app_ci.container = rg
        self.site_name = self.web_app_ci.appName
        web_site_zip = File(Thread.currentThread().getContextClassLoader().getResource("web_site.zip").toURI())
        self.web_app_ci.file = web_site_zip
        self.client.create_resource_group(rg.resourceName, rg.resourceLocation)
        define_app_service_plan.create_or_update(plan, rg)

    @classmethod
    def tearDownClass(self):
        self.client.destroy_resource_group(self.resource_group)

    def test_web_app(self):
        self.assertFalse(self.client.website_exists(self.resource_group, self.site_name))
        define_web_app.create_or_update(self.web_app_ci, self.web_app_ci.container)
        self.assertTrue(self.client.website_exists(self.resource_group, self.site_name))

        app_settings = self.client.get_app_settings(self.resource_group, self.site_name)
        self.assertEqual(app_settings['mykey'], "myvalue")

        connection_strings = self.client.get_connection_strings(self.resource_group, self.site_name)
        self.assertEqual(len(connection_strings), 1)
        connection_string_info = connection_strings[0]
        self.assertEqual(connection_string_info.getName(), "test_connection")
        self.assertEqual(connection_string_info.getConnectionString(), "some string connection")
        # Azure returns None the the type field. Ignore the assertion
        # self.assertEqual(connection_string_info.getType(), DatabaseServerType.Custom)

        upload_web_app_artifact.upload(self.web_app_ci, self.web_app_ci.container)

        remove_web_app.destroy(self.web_app_ci, self.web_app_ci.container)
        # Azure does not clean up right away
        time.sleep(10)
        self.assertFalse(self.client.website_exists(self.resource_group, self.site_name))





