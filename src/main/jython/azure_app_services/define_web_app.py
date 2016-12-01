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
