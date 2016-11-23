from com.microsoft.azure.management.resources import ResourceManagementService
from com.microsoft.azure.management.resources.models import ResourceGroup, ResourceGroupListParameters

from com.microsoft.windowsazure.exception import ServiceException

from com.microsoft.windowsazure.management.configuration import ManagementConfiguration

from com.microsoft.azure.management.websites import WebSiteManagementService
from com.microsoft.azure.management.websites.models import WebHostingPlan, WebHostingPlanCreateOrUpdateParameters
from com.microsoft.azure.management.websites.models import WebSiteBaseProperties, WebSiteBase, WebHostingPlanProperties
from com.microsoft.azure.management.websites.models import WebSiteNameValueParameters, NameValuePair, WebSiteCreateOrUpdateParameters
from com.microsoft.azure.management.websites.models import ConnectionStringInfo, WorkerSizeOptions, WebSiteState, SkuOptions
from com.microsoft.azure.management.websites.models import WebSiteUpdateConnectionStringsParameters, WebSiteGetParameters
from com.microsoft.azure.management.websites.models import WebSiteDeleteParameters, DatabaseServerType

from com.microsoft.azure.utility import AuthHelper

from java.net import URI
from java.io import File
from java.util import HashMap, ArrayList
from java.net import SocketTimeoutException

from okhttp3 import OkHttpClient, Credentials, MediaType

import time


# Gateway to Azure.
# Uses the Azure Java SDK version 0.9. https://github.com/Azure/azure-sdk-for-java/tree/0.9
from okhttp3 import Request
from okhttp3 import RequestBody


class AzureClient:
    def __init__(self, subscription_id, tenant_id, client_id, client_key, ftp_user, ftp_password, base_url, management_url,
                 active_directory_url):
        self.subscription_id = subscription_id
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_key = client_key
        self.ftp_user = ftp_user
        self.ftp_password = ftp_password
        self.base_url = URI(base_url)
        self.management_url = management_url
        self.active_directory_url = active_directory_url
        self._access_token = None
        self._zip_media_type = MediaType.parse("application/zip")
        self._json_media_type = MediaType.parse("application/json")

    @staticmethod
    def new_instance(ci):
        return AzureClient(ci.subscriptionId, ci.tenantId, ci.clientId, ci.clientKey, ci.ftpUser, ci.ftpPassword,
                           ci.azureBaseURL, ci.azureManagementURL, ci.azureActiveDirectoryURL)

    def _create_config(self):
        return ManagementConfiguration.configure(None, self.base_url, self.subscription_id, self._resolve_access_token())

    def _resolve_access_token(self):
        # TODO: Add JVM caching for token.  Tokens last up to an hour
        if not self._access_token:
            creds = AuthHelper.getAccessTokenFromServicePrincipalCredentials(self.management_url, self.active_directory_url,
                                                                             self.tenant_id, self.client_id, self.client_key)
            self._access_token = creds.getAccessToken()
        return self._access_token

    def _resource_management_client(self):
        return ResourceManagementService.create(self._create_config())

    def _website_management_client(self):
        return WebSiteManagementService.create(self._create_config())

    def _resource_group_operations(self):
        return self._resource_management_client().getResourceGroupsOperations()

    def _web_hosting_plans_operations(self):
        return self._website_management_client().getWebHostingPlansOperations()

    def _web_site_operations(self):
        return self._website_management_client().getWebSitesOperations()

    def _get_ftp_basic_auth(self):
        return Credentials.basic(self.ftp_user, self.ftp_password)

    def list_resource_groups(self):
        operations = self._resource_group_operations()
        params = ResourceGroupListParameters()
        result = operations.list(params)
        return [r.getName() for r in result.getResourceGroups()]

    def create_resource_group(self, name, location, tags=None):
        operations = self._resource_group_operations()
        params = ResourceGroup()
        params.setLocation(location)
        if tags:
            tags_as_map = HashMap()
            tags_as_map.putAll(tags)
            params.setTags(tags_as_map)
        operations.createOrUpdate(name, params)

    def resource_group_exists(self, name):
        try:
            self._resource_group_operations().get(name)
        except ServiceException, e:
            if e.getMessage().startswith("ResourceGroupNotFound:"):
                return False
            else:
                raise e
        return True

    def destroy_resource_group(self, name):
        if self.resource_group_exists(name):
            self._resource_group_operations().delete(name)
            return True
        return False

    def create_app_service_plan(self, resource_group, name, location, sku, worker_size):
        hosting_plan_parameters = WebHostingPlanCreateOrUpdateParameters()
        plan = WebHostingPlan()
        plan.setLocation(location)
        plan.setName(name)
        plan_properties = WebHostingPlanProperties()
        plan_properties.setSku(SkuOptions.valueOf(str(sku)))
        plan_properties.setWorkerSize(WorkerSizeOptions.valueOf(str(worker_size)))
        plan.setProperties(plan_properties)
        hosting_plan_parameters.setWebHostingPlan(plan)
        self._web_hosting_plans_operations().createOrUpdate(resource_group, hosting_plan_parameters)

    def app_service_plan_exists(self, resource_group, name):
        try:
            self._web_hosting_plans_operations().get(resource_group, name)
        except ServiceException:
            return False
        return True

    def destroy_app_service_plan(self, resource_group, name):
        if self.app_service_plan_exists(resource_group, name):
            self._web_hosting_plans_operations().delete(resource_group, name)
            return True
        return False

    def create_website(self, resource_group, site_name, location, service_plan):
        parameters = WebSiteCreateOrUpdateParameters()
        web = WebSiteBase()
        web.setLocation(location)
        properties = WebSiteBaseProperties()
        properties.setServerFarm(service_plan)
        web.setProperties(properties)
        parameters.setWebSite(web)
        self._web_site_operations().createOrUpdate(resource_group, site_name, None, parameters)

    def _get_website_state(self, resource_group, site_name):
        response = self._web_site_operations().get(resource_group, site_name, None, WebSiteGetParameters())
        return response.getWebSite().getProperties().getState()

    def stop_website(self, resource_group, site_name):
        if self._get_website_state(resource_group, site_name) != WebSiteState.Stopped:
            self._web_site_operations().stop(resource_group, site_name, None)

    def start_website(self, resource_group, site_name):
        if self._get_website_state(resource_group, site_name) != WebSiteState.Running:
            self._web_site_operations().start(resource_group, site_name, None)

    def website_exists(self, resource_group, site_name):
        try:
            self._web_site_operations().get(resource_group, site_name, None, None)
        except ServiceException:
            return False
        return True

    def destroy_website(self, resource_group, site_name):
        if self.website_exists(resource_group, site_name):
            params = WebSiteDeleteParameters()
            params.setDeleteEmptyServerFarm(False)
            params.setDeleteAllSlots(True)
            self._web_site_operations().delete(resource_group, site_name, None, params)
            return True
        return False

    def update_app_settings(self, resource_group, site_name, location, settings):
        nv_pairs_list = ArrayList()
        for key, value in settings.items():
            vp = NameValuePair()
            vp.setName(key)
            vp.setValue(value)
            nv_pairs_list.add(vp)
        wsnv_params = WebSiteNameValueParameters()
        wsnv_params.setProperties(nv_pairs_list)
        wsnv_params.setLocation(location)
        self._web_site_operations().updateAppSettings(resource_group, site_name, None, wsnv_params)

    def get_app_settings(self, resource_group, site_name):
        settings = self._web_site_operations().getAppSettings(resource_group, site_name, None)
        result = {}
        for name_value_pair in settings.getResource().getProperties():
            result[name_value_pair.getName()] = name_value_pair.getValue()
        return result

    def update_db_conn_settings(self, resource_group, site_name, location, conn_name, conn_string, conn_type):
        csi = ConnectionStringInfo()
        csi.setName(conn_name)
        csi.setConnectionString(conn_string)
        csi.setType(DatabaseServerType.valueOf(str(conn_type)))
        conn_string_infos_list = ArrayList()
        conn_string_infos_list.add(csi)
        conn_params = WebSiteUpdateConnectionStringsParameters()
        conn_params.setProperties(conn_string_infos_list)
        conn_params.setLocation(location)
        self._web_site_operations().updateConnectionStrings(resource_group, site_name, None, conn_params)

    def get_connection_strings(self, resource_group, site_name):
        settings = self._web_site_operations().getConnectionStrings(resource_group, site_name, None)
        return settings.getResource().getProperties()

    @staticmethod
    def _check_return_code(response):
        rc = response.code()
        if rc != 200 and rc != 201:
            msg = "rc=%s" % rc
            if response.body() is not None:
                msg = "%s msg=%s" % (msg, response.body().string())
            raise Exception(msg)

    @staticmethod
    def _build_kudu_service_url(site_name, service_uri):
        return "https://%s.scm.azurewebsites.net/api/%s" % (site_name, service_uri)

    @staticmethod
    def _kudu_request(site_name, service_uri):
        return Request.Builder().url(AzureClient._build_kudu_service_url(site_name, service_uri))

    def _execute_http_request(self, request_builder, error_checking=True):
        ok_http_client = OkHttpClient()
        request = request_builder.addHeader("Authorization", self._get_ftp_basic_auth()).build()
        response = ok_http_client.newCall(request).execute()
        if error_checking:
            AzureClient._check_return_code(response)
        else:
            return response.code() == 200 or response.code() == 201

    def wait_for_kudu_services(self, site_name):
        retry_count = 0
        while retry_count < 12:
            if self.is_kudu_services_available(site_name):
                return
            retry_count += 1
            time.sleep(5)
        raise Exception("Azure Kudu Services for web app [%s] unavailable after a minute of waiting. Retry is a while." % site_name)

    def is_kudu_services_available(self, site_name):
        try:
            request = self._kudu_request(site_name, "vfs/site")
            return self._execute_http_request(request, error_checking=False)
        except SocketTimeoutException:
            return False

    def upload_website(self, site_name, zip_file_path):
        body = RequestBody.create(self._zip_media_type, File(zip_file_path))
        request = self._kudu_request(site_name, "zip/site/wwwroot").put(body)
        self._execute_http_request(request)

    def deploy_triggered_webjob(self, webjob_name, site_name, executable_file_name, schedule, zip_file_path):
        body = RequestBody.create(self._zip_media_type, File(zip_file_path))
        request = self._kudu_request(site_name, "triggeredwebjobs/%s" % webjob_name).put(body)\
            .addHeader("Content-Disposition", "attachement; filename=%s" % executable_file_name)
        self._execute_http_request(request)
        if schedule:
            self.update_triggered_webjob_schedule(webjob_name, site_name, schedule)

    def update_triggered_webjob_schedule(self, webjob_name, site_name, schedule):
        body = RequestBody.create(self._json_media_type, '{ "schedule": "%s"}' % schedule)
        request = self._kudu_request(site_name, "triggeredwebjobs/%s/settings" % webjob_name).put(body)
        self._execute_http_request(request)

    def remove_triggered_webjob(self, webjob_name, site_name):
        request = self._kudu_request(site_name, "triggeredwebjobs/%s" % webjob_name).delete()
        self._execute_http_request(request)

    def triggered_webjob_exists(self, webjob_name, site_name):
        request = self._kudu_request(site_name, "triggeredwebjobs/%s" % webjob_name)
        return self._execute_http_request(request, error_checking=False)

