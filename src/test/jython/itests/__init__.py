import os
from com.microsoft.azure.management.websites.models import SkuOptions, WorkerSizeOptions, DatabaseServerType


class CiStub(object):

    def getProperty(self, name):
        return self.__dict__[name]


class SubscriptionCi(CiStub):
    def __init__(self):
        self.name = "MyAzureSubscription"
        self.id = "Infrastructure/%s" % self.name
        self.type = "azure.Subscription"
        self.subscriptionId = None
        self.tenantId = None
        self.clientId = None
        self.clientKey = None
        self.ftpUser = None
        self.ftpPassword = None
        self.azureBaseURL = "https://management.azure.com/"
        self.azureManagementURL = "https://management.core.windows.net/"
        self.azureActiveDirectoryURL = "https://login.windows.net/"
        self._init_from_file();

    def _init_from_file(self):
        file_location = os.getenv('azure_subscription_conf')
        if not file_location:
            raise Exception("No environment variable named 'azure_subscription_conf' set.")
        with open(file_location, 'r') as inf:
            settings = eval(inf.read())
            self.subscriptionId = settings["subscriptionId"]
            self.tenantId = settings["tenantId"]
            self.clientId = settings["clientId"]
            self.clientKey = settings["clientKey"]
            self.ftpUser = settings["ftpUser"]
            self.ftpPassword = settings["ftpPassword"]


class ResourceGroupCi(CiStub):
    def __init__(self):
        self.name = "MyAzureResource"
        self.id = "Infrastructure/MyAzureSubscription/%s" % self.name
        self.type = "azure.ResourceGroup"
        self.subscription = SubscriptionCi()
        self.resourceName = "xld_azure_app_service_plugin_tests"
        self.resourceLocation = "westeurope"
        self.resourceTags = {'myTag': 'myTagValue'}


class AppServicePlanCi(CiStub):
    def __init__(self):
        self.name = "MyAppServicePlan"
        self.id = "Infrastructure/MyAzureSubscription/MyAzureResource/%s" % self.name
        self.type = "azure.AppServicePlan"
        self.servicePlanName = "xld_azure_app_service_plugin_basic_plan"
        self.location = "westeurope"
        self.sku = SkuOptions.Basic
        self.workerSize = WorkerSizeOptions.Small


class WebAppCi(CiStub):
    def __init__(self):
        self.name = "MyWebApp"
        self.id = "Infrastructure/MyAzureSubscription/MyAzureResource/%s" % self.name
        self.type = "azure.WebAppModule"
        self.appName = "xld-azure-app-service-plugin-webapp"
        self.plan = "xld_azure_app_service_plugin_basic_plan"
        self.appSettings = {"mykey": "myvalue"}
        self.sqlDatabaseConnectionStrings = {"mykey1": "myvalue"}
        self.sqlServerConnectionStrings = {"mykey2": "myvalue"}
        self.customConnectionStrings = {"mykey3": "myvalue"}


class TriggeredWebJobCi(CiStub):
    def __init__(self):
        self.name = "MyWebJob"
        self.id = "Infrastructure/MyAzureSubscription/MyAzureResource/%s" % self.name
        self.type = "azure.TriggeredWebJobModule"
        self.webJobName = "xld-webjob"
        self.executableFileName = "echo.sh"
        self.appName = "xld-azure-app-service-plugin-webapp"
        self.schedule = "0 */10 * * * *"


