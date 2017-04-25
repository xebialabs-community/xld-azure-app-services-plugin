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

from azure_app_services.client import AzureClient
from itests import ResourceGroupCi, AppServicePlanCi, WebAppCi, TriggeredWebJobCi, ContinuousWebJobCi
from azure_app_services import define_app_service_plan, define_web_app, deploy_triggered_web_job, remove_triggered_web_job
from azure_app_services import deploy_continuous_web_job, remove_continuous_web_job, stop_continuous_web_job

from java.lang import Thread
from java.io import File


class WebJobTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        rg = ResourceGroupCi()
        self.resource_group = rg.resourceName
        self.client = AzureClient.new_instance(rg.subscription)

        webjob_ci = TriggeredWebJobCi()
        webjob_ci.container = rg
        webjob_ci.file = File(Thread.currentThread().getContextClassLoader().getResource("webjob.zip").toURI())

        continuous_webjob_ci = ContinuousWebJobCi()
        continuous_webjob_ci.container = rg
        continuous_webjob_ci.file = File(Thread.currentThread().getContextClassLoader().getResource("continuous_webjob.zip").toURI())

        webapp_ci = WebAppCi()
        webapp_ci.appSettings = {}
        webapp_ci.customConnectionStrings = {}
        webapp_ci.sqlServerConnectionStrings = {}
        webapp_ci.sqlDatabaseConnectionStrings = {}

        self.client.create_resource_group(rg.resourceName, rg.resourceLocation)
        define_app_service_plan.create_or_update(AppServicePlanCi(), rg)
        define_web_app.create_or_update(webapp_ci, rg)

        self.client.wait_for_kudu_services(webjob_ci.appName)

        self.webjob = webjob_ci.webJobName
        self.site_name = webjob_ci.appName
        self.webjob_ci = webjob_ci

        self.continuous_webjob_ci = continuous_webjob_ci
        self.continuous_webjob = continuous_webjob_ci.webJobName

    @classmethod
    def tearDownClass(self):
        self.client.destroy_resource_group(self.resource_group)

    def test_trigger_web_job(self):
        self.assertFalse(self.client.triggered_webjob_exists(self.webjob, self.site_name))
        deploy_triggered_web_job.create_or_update(self.webjob_ci, self.webjob_ci.container)
        self.assertTrue(self.client.triggered_webjob_exists(self.webjob, self.site_name))
        remove_triggered_web_job.destroy(self.webjob_ci, self.webjob_ci.container)
        # Azure does not clean up right away
        time.sleep(10)
        self.assertFalse(self.client.triggered_webjob_exists(self.webjob, self.site_name))

    def test_continuous_web_job(self):
        self.assertFalse(self.client.continuous_webjob_exists(self.continuous_webjob, self.site_name))
        deploy_continuous_web_job.create_or_update(self.continuous_webjob_ci, self.continuous_webjob_ci.container)
        self.assertTrue(self.client.continuous_webjob_exists(self.continuous_webjob, self.site_name))
        time.sleep(5)
        self.assertEqual(self.client.continuous_webjob_status(self.continuous_webjob, self.site_name), "Running")
        stop_continuous_web_job.stop(self.continuous_webjob_ci, self.continuous_webjob_ci.container)
        time.sleep(10)
        self.assertEqual(self.client.continuous_webjob_status(self.continuous_webjob, self.site_name), "Stopped")

        remove_continuous_web_job.destroy(self.continuous_webjob_ci, self.continuous_webjob_ci.container)
        # Azure does not clean up right away
        time.sleep(10)
        self.assertFalse(self.client.continuous_webjob_exists(self.continuous_webjob, self.site_name))




