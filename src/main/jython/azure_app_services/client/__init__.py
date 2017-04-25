#
# Copyright 2017 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

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
from com.microsoft.azure.management.websites.models import WebSiteUpdateConfigurationDetails, WebSiteUpdateConfigurationParameters

from com.microsoft.azure.utility import AuthHelper

from java.net import URI
from java.io import File
from java.util import HashMap, ArrayList
from java.net import SocketTimeoutException

from okhttp3 import OkHttpClient, Credentials, MediaType

import time
import json


# Gateway to Azure.
# Uses the Azure Java SDK version 0.9. https://github.com/Azure/azure-sdk-for-java/tree/0.9
from okhttp3 import Request
from okhttp3 import RequestBody


class WebAppGeneralSettings(object):
    def __init__(self, platform_32bit=True, always_on=False, net_framework_version="", php_version="", python_version="",
                 java_version="", java_container="TOMCAT", java_container_version=""):
        self.platform_32bit = platform_32bit
        self.always_on = always_on
        self.net_framework_version = net_framework_version
        self.php_version = php_version
        self.python_version = python_version
        self.java_version = java_version
        self.java_container = java_container
        self.java_container_version = java_container_version


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
        self._creds = Credentials.basic(self.ftp_user, self.ftp_password)

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

    def update_general_settings(self, resource_group, site_name, location, settings):
        wsuc_details = WebSiteUpdateConfigurationDetails()
        wsuc_details.setUse32BitWorkerProcess(settings.platform_32bit)
        wsuc_details.setAlwaysOn(settings.always_on)
        if settings.java_version:
            wsuc_details.setNetFrameworkVersion("")
            wsuc_details.setPhpVersion("")
            wsuc_details.setPythonVersion("")
            if not settings.java_container:
                raise Exception("Java Container required.")
            wsuc_details.setJavaContainer(settings.java_container)
            if not settings.java_container_version:
                raise Exception("Java Container Version required.")
            wsuc_details.setJavaContainerVersion(settings.java_container_version)
            wsuc_details.setJavaVersion(settings.java_version)
        else:
            wsuc_details.setNetFrameworkVersion(settings.net_framework_version)
            wsuc_details.setPhpVersion(settings.php_version)
            wsuc_details.setPythonVersion(settings.python_version)

        wsuc_params = WebSiteUpdateConfigurationParameters()
        wsuc_params.setProperties(wsuc_details)
        wsuc_params.setLocation(location)
        self._web_site_operations().updateConfiguration(resource_group, site_name, None, wsuc_params)

    def get_general_settings(self, resource_group, site_name):
        result = self._web_site_operations().getConfiguration(resource_group, site_name, None, None)
        props = result.getResource().getProperties()
        settings = WebAppGeneralSettings()
        settings.platform_32bit = props.isUse32BitWorkerProcess()
        settings.java_version = props.getJavaVersion()
        settings.java_container = props.getJavaContainer()
        settings.java_container_version = props.getJavaContainerVersion()
        # settings.always_on has no associated value in the props :( Check if in meta-data maybe???
        settings.net_framework_version = props.getNetFrameworkVersion()
        settings.php_version = props.getPhpVersion()
        settings.python_version = props.getPythonVersion()
        return settings

    @staticmethod
    def _new_connection_string_info(name, value, db_server_type):
        csi = ConnectionStringInfo()
        csi.setName(name)
        csi.setConnectionString(value)
        csi.setType(db_server_type)
        return csi

    def update_db_conn_settings(self, resource_group, site_name, location,
                                sql_database_conn_strings, sql_server_conn_strings, custom_conn_string):
        conn_string_infos_list = ArrayList()
        constructor = self._new_connection_string_info
        for key, value in sql_database_conn_strings.items():
            conn_string_infos_list.add(constructor(key, value, DatabaseServerType.SQLAzure))
        for key, value in sql_server_conn_strings.items():
            conn_string_infos_list.add(constructor(key, value, DatabaseServerType.SQLServer))
        for key, value in custom_conn_string.items():
            conn_string_infos_list.add(constructor(key, value, DatabaseServerType.Custom))
        conn_params = WebSiteUpdateConnectionStringsParameters()
        conn_params.setProperties(conn_string_infos_list)
        conn_params.setLocation(location)
        self._web_site_operations().updateConnectionStrings(resource_group, site_name, None, conn_params)

    def get_connection_strings(self, resource_group, site_name):
        settings = self._web_site_operations().getConnectionStrings(resource_group, site_name, None)
        return settings.getResource().getProperties()

    @staticmethod
    def _check_return_code(response, reply_body=None):
        rc = response.code()
        if rc != 200 and rc != 201:
            msg = "rc=%s" % rc
            if reply_body is not None:
                msg = "%s msg=%s" % (msg, reply_body)
            elif response.body() is not None:
                try:
                    msg = "%s msg=%s" % (msg, response.body().string())
                finally:
                    response.body().close()
            raise Exception(msg)

    @staticmethod
    def _build_kudu_service_url(site_name, service_uri):
        return "https://%s.scm.azurewebsites.net/api/%s" % (site_name, service_uri)

    @staticmethod
    def _kudu_request(site_name, service_uri):
        return Request.Builder().url(AzureClient._build_kudu_service_url(site_name, service_uri))

    def _execute_http_request(self, request_builder, error_checking=True):
        response = self._execute_http_request_return_response(request_builder)
        if error_checking:
            AzureClient._check_return_code(response)
        else:
            if response.code() == 200 or response.code() == 201:
                return 0
            else:
                return response.code()

    def _execute_http_request_return_response(self, request_builder):
        ok_http_client = OkHttpClient()
        request = request_builder.addHeader("Authorization", self._creds).build()
        return ok_http_client.newCall(request).execute()

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
            request = self._kudu_request(site_name, "vfs/site").get()
            return self._execute_http_request(request, error_checking=False)
        except SocketTimeoutException:
            return 504

    def upload_website(self, site_name, zip_file_path):
        body = RequestBody.create(self._zip_media_type, File(zip_file_path))
        request = self._kudu_request(site_name, "zip/site/wwwroot").put(body)
        self._execute_http_request(request)

    def _deploy_webjob(self, webjob_name, site_name, executable_file_name, zip_file_path, webjob_service_type="triggeredwebjobs" ):
        body = RequestBody.create(self._zip_media_type, File(zip_file_path))
        request = self._kudu_request(site_name, "%s/%s" % (webjob_service_type, webjob_name)).put(body) \
            .addHeader("Content-Disposition", "attachement; filename=%s" % executable_file_name)
        self._execute_http_request(request)

    def deploy_continuous_webjob(self, webjob_name, site_name, executable_file_name, is_singleton, zip_file_path):
        self._deploy_webjob(webjob_name, site_name, executable_file_name, zip_file_path, webjob_service_type="continuouswebjobs")
        singleton_string = "true" if is_singleton else "false"
        body = '{ "is_singleton": %s }' % singleton_string
        self._update_webjob_setting(webjob_name, site_name, body, webjob_service_type="continuouswebjobs")

    def deploy_triggered_webjob(self, webjob_name, site_name, executable_file_name, schedule, zip_file_path):
        self._deploy_webjob(webjob_name, site_name, executable_file_name, zip_file_path)
        if schedule:
            body = '{ "schedule": "%s"}' % schedule
            self._update_webjob_setting(webjob_name, site_name, body)

    def _update_webjob_setting(self, webjob_name, site_name, json_body, webjob_service_type="triggeredwebjobs"):
        body = RequestBody.create(self._json_media_type, json_body)
        request = self._kudu_request(site_name, "%s/%s/settings" % (webjob_service_type, webjob_name)).put(body)
        self._execute_http_request(request)

    def remove_triggered_webjob(self, webjob_name, site_name):
        request = self._kudu_request(site_name, "triggeredwebjobs/%s" % webjob_name).delete()
        self._execute_http_request(request)

    def remove_continuous_webjob(self, webjob_name, site_name):
        request = self._kudu_request(site_name, "continuouswebjobs/%s" % webjob_name).delete()
        self._execute_http_request(request)

    def triggered_webjob_exists(self, webjob_name, site_name):
        request = self._kudu_request(site_name, "triggeredwebjobs/%s" % webjob_name)
        return self._execute_http_request(request, error_checking=False)

    def continuous_webjob_exists(self, webjob_name, site_name):
        request = self._kudu_request(site_name, "continuouswebjobs/%s" % webjob_name)
        return self._execute_http_request(request, error_checking=False)

    def continuous_webjob_status(self, webjob_name, site_name):
        request = self._kudu_request(site_name, "continuouswebjobs/%s" % webjob_name)
        response = self._execute_http_request_return_response(request)
        self._check_return_code(response)
        reply = json.loads(str(response.body().string()))
        response.body().close()
        return reply["status"]

    def _retry_stop_start_webjob(self, site_name, service_uri):
        retry = 0
        while retry < 12:
            body = RequestBody.create(self._json_media_type, "")
            request = self._kudu_request(site_name, service_uri).post(body)
            response = self._execute_http_request_return_response(request)
            reply_body = str(response.body().string())
            response.body().close()
            if response.code() == 404 and reply_body.startswith('"No route registered for'):
                retry += 1
                time.sleep(5)
            else:
                self._check_return_code(response, reply_body)
                return True
        raise Exception("rc=404, msg='No route registered for 'api/%s''" % service_uri)

    def start_continuous_webjob(self, webjob_name, site_name):
        status = self.continuous_webjob_status(webjob_name, site_name)
        if status == 'Stopped':
            return self._retry_stop_start_webjob(site_name, "continuouswebjobs/%s/start" % webjob_name)
        return False

    def stop_continuous_webjob(self, webjob_name, site_name):
        status = self.continuous_webjob_status(webjob_name, site_name)
        if status != 'Stopped':
            return self._retry_stop_start_webjob(site_name, "continuouswebjobs/%s/stop" % webjob_name)
        return False



