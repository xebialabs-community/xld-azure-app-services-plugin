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
        ci.setProperty("appSettings", app_settings)
        conn_strings = client.get_connection_strings(resource_group, ws.name)
        custom_conn_strings = {}
        for conn_string in conn_strings:
            custom_conn_strings[conn_string.name] = conn_string.connectionString
        ci.setProperty("customConnectionStrings", custom_conn_strings)
        settings = client.get_general_settings(resource_group, ws.name)
        ci.setProperty("platform32bit", settings.platform_32bit)
        ci.setProperty("javaVersion", settings.java_version)
        ci.setProperty("javaContainer", settings.java_container)
        ci.setProperty("javaContainerVersion", settings.java_container_version)
        ci.setProperty("netFrameworkVersion", settings.net_framework_version)
        ci.setProperty("phpVersion", settings.php_version)
        ci.setProperty("pythonVersion", settings.python_version)
        discovered(ci, ctx)


def discover_resource_groups(client, ctx, descriptor, webapp_descriptor, base_id):
    resource_groups = client.list_resource_groups();
    print "Discovered %s resource groups" % (len(resource_groups))
    for rg in resource_groups:
        ci = descriptor.newInstance("%s/%s" % (base_id, rg.getName()))
        ci.setProperty("resourceLocation", rg.getLocation())
        ci.setProperty("resourceName", rg.getName())
        ci.setProperty("resourceTags", rg.getTags())
        discovered(ci, ctx)
    [discover_webapps(client, ctx,webapp_descriptor, "%s/%s" % (base_id, rg.name), rg.name) for rg in resource_groups]


def perform_discovery(subscription, ctx, resource_group_descriptor, web_app_module_descriptor):
    client = AzureClient.new_instance(subscription)
    discover_resource_groups(client, ctx, resource_group_descriptor, web_app_module_descriptor, subscription.id)


if __name__ == '__main__' or __name__ == '__builtin__':
    print "Starting discovery of resource groups and web apps"
    resource_group_descriptor = Type.valueOf("azure.ResourceGroup").getDescriptor()
    web_app_module_descriptor = Type.valueOf("azure.WebAppModule").getDescriptor()
    # if XLD sugar utility wrappers available use it to
    if wrap:
        thisCi = wrap(thisCi)
    perform_discovery(thisCi, inspectionContext, resource_group_descriptor, web_app_module_descriptor)
