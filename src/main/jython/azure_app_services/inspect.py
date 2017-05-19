#
# Copyright 2017 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

from azure_app_services.client import AzureClient
from com.xebialabs.deployit.plugin.api.reflect import Type


def discovered(ci, ctx):
    ctx.discovered(ci)
    ctx.inspected(ci)


def discover_webapps(client, ctx, descriptor, base_id, resource_group):
    websites = client.list_websites(resource_group)
    print "Discovered %s web apps for resource group %s" % (len(websites), resource_group)
    for ws in websites:
        print "Inspecting properties for %s web app" % (ws.name)
        ci = descriptor.newInstance("%s/%s" % (base_id, ws.name))
        ci.setProperty("appName", ws.name)
        ci.setProperty("plan", ws.getProperties().getServerFarm())
        app_settings = client.get_app_settings(resource_group, ws.name)
        if "WEBSITE_NODE_DEFAULT_VERSION" in app_settings.keys():
            app_settings.pop("WEBSITE_NODE_DEFAULT_VERSION", None)
        ci.setProperty("appSettings", app_settings)
        conn_strings = client.get_connection_strings(resource_group, ws.name)
        custom_conn_strings = {}
        for conn_string in conn_strings:
            custom_conn_strings[conn_string.name] = conn_string.connectionString
        ci.setProperty("customConnectionStrings", custom_conn_strings)
        settings = client.get_general_settings(resource_group, ws.name)
        set_non_empty_property(ci, "platform32bit", settings.platform_32bit)
        set_non_empty_property(ci, "javaVersion", settings.java_version)
        set_non_empty_property(ci, "javaContainer", settings.java_container)
        set_non_empty_property(ci, "javaContainerVersion", settings.java_container_version)
        set_non_empty_property(ci, "netFrameworkVersion", settings.net_framework_version)
        set_non_empty_property(ci, "phpVersion", settings.php_version)
        set_non_empty_property(ci, "pythonVersion", settings.python_version)
        discovered(ci, ctx)


def discover_service_plans(client, ctx, descriptor, base_id, resource_group):
    plans = client.list_service_plans(resource_group)
    print "Discovered %s service plans for resource group %s" % (len(plans), resource_group)
    for sp in plans:
        print "Inspecting properties for %s service plan" % (sp.name)
        ci = descriptor.newInstance("%s/%s" % (base_id, sp.name))
        ci.setProperty("servicePlanName", sp.name)
        ci.setProperty("location", sp.location)
        ci.setProperty("workerSize", sp.getProperties().getWorkerSize())
        ci.setProperty("sku", sp.getProperties().getSku())
        discovered(ci, ctx)


def set_non_empty_property(ci, name, value):
    if value is not None and len(str(value).strip()) > 0:
        ci.setProperty(name, value)


def discover_resource_groups(client, ctx, descriptor, webapp_descriptor, service_plan_descriptor, base_id):
    resource_groups = client.list_resource_groups()
    print "Discovered %s resource groups" % (len(resource_groups))
    for rg in resource_groups:
        ci = descriptor.newInstance("%s/%s" % (base_id, rg.getName()))
        ci.setProperty("resourceLocation", rg.getLocation())
        ci.setProperty("resourceName", rg.getName())
        ci.setProperty("resourceTags", rg.getTags())
        discovered(ci, ctx)
    [discover_webapps(client, ctx,webapp_descriptor, "%s/%s" % (base_id, rg.name), rg.name) for rg in resource_groups]
    [discover_service_plans(client, ctx, service_plan_descriptor, "%s/%s" % (base_id, rg.name), rg.name) for rg in resource_groups]


def perform_discovery(subscription, ctx, resource_group_descriptor, web_app_module_descriptor, service_plan_descriptor):
    client = AzureClient.new_instance(subscription)
    discover_resource_groups(client, ctx, resource_group_descriptor, web_app_module_descriptor, service_plan_descriptor, subscription.id)


if __name__ == '__main__' or __name__ == '__builtin__':
    print "Starting discovery of resource groups and web apps"
    resource_group_descriptor = Type.valueOf("azure.ResourceGroup").getDescriptor()
    web_app_module_descriptor = Type.valueOf("azure.WebAppModule").getDescriptor()
    service_plan_descriptor = Type.valueOf("azure.AppServicePlan").getDescriptor()
    # if XLD sugar utility wrappers available use it to
    if wrap:
        thisCi = wrap(thisCi)
    perform_discovery(thisCi, inspectionContext, resource_group_descriptor, web_app_module_descriptor, service_plan_descriptor)
