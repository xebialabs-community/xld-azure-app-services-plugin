import unittest
import time
from com.microsoft.azure.management.websites.models import DatabaseServerType

from azure_app_services.client import AzureClient
from itests import ResourceGroupCi, AppServicePlanCi, WebAppCi, TriggeredWebJobCi
from azure_app_services import define_app_service_plan, define_web_app, deploy_triggered_web_job, remove_triggered_web_job

from java.lang import Thread
from java.io import File


class TriggeredWebJobTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        rg = ResourceGroupCi()
        self.resource_group = rg.resourceName
        self.client = AzureClient.new_instance(rg.subscription)
        webjob_ci = TriggeredWebJobCi()
        webjob_ci.container = rg
        webjob_ci.file = File(Thread.currentThread().getContextClassLoader().getResource("webjob.zip").toURI())

        webapp_ci = WebAppCi()
        webapp_ci.appSettings = {}
        webapp_ci.connectionName = None

        #self.client.create_resource_group(rg.resourceName, rg.resourceLocation)
        #define_app_service_plan.create_or_update(AppServicePlanCi(), rg)
        #define_web_app.create_or_update(webapp_ci, rg)
        self.client.wait_for_kudu_services(webjob_ci.appName)
        self.webjob = webjob_ci.webJobName
        self.site_name = webjob_ci.appName
        self.webjob_ci = webjob_ci

    @classmethod
    def tearDownClass(self):
        # self.client.destroy_resource_group(self.resource_group)
        pass

    def test_web_job(self):
        self.assertFalse(self.client.triggered_webjob_exists(self.webjob, self.site_name))
        deploy_triggered_web_job.create_or_update(self.webjob_ci, self.webjob_ci.container)
        self.assertTrue(self.client.triggered_webjob_exists(self.webjob, self.site_name))
        remove_triggered_web_job.destroy(self.webjob_ci, self.webjob_ci.container)
        # Azure does not clean up right away
        time.sleep(10)
        self.assertFalse(self.client.triggered_webjob_exists(self.webjob, self.site_name))





