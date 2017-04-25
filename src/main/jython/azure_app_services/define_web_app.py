#
# Copyright 2017 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

from azure_app_services.client import AzureClient, WebAppGeneralSettings


def to_general_settings(deployed):
    return WebAppGeneralSettings(platform_32bit=deployed.platform32bit, always_on=deployed.alwaysOn, net_framework_version=deployed.netFrameworkVersion,
                                 php_version=deployed.phpVersion, python_version=deployed.pythonVersion,
                                 java_version=deployed.javaVersion, java_container=deployed.javaContainer, java_container_version=deployed.javaContainerVersion)


def create_or_update(deployed, container):
    client = AzureClient.new_instance(container.subscription)
    print "Defining web site [%s] in resource group [%s]" % (deployed.appName, container.resourceName)
    client.create_website(container.resourceName, deployed.appName, container.resourceLocation, deployed.plan)
    print "Updating general settings"
    client.update_general_settings(container.resourceName, deployed.appName, container.resourceLocation, to_general_settings(deployed))
    if deployed.appSettings.keys():
        print "Updating app settings"
        client.update_app_settings(container.resourceName, deployed.appName, container.resourceLocation, deployed.appSettings)

    if deployed.sqlDatabaseConnectionStrings.keys() or deployed.sqlServerConnectionStrings.keys() or deployed.customConnectionStrings.keys():
        print "Updating connection strings"
        client.update_db_conn_settings(container.resourceName, deployed.appName, container.resourceLocation,
                                       deployed.sqlDatabaseConnectionStrings, deployed.sqlServerConnectionStrings,
                                       deployed.customConnectionStrings)
    print "Done"

if __name__ == '__main__' or __name__ == '__builtin__':
    create_or_update(deployed, deployed.container)
