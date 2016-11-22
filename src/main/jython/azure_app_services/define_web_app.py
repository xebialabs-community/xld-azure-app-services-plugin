from azure_app_services.client import AzureClient


def create_or_update(deployed, container):
    client = AzureClient.new_instance(container.subscription)
    print "Defining web site [%s] in resource group [%s]" % (deployed.appName, container.resourceName)
    client.create_website(container.resourceName, deployed.appName, container.resourceLocation, deployed.plan)

    if deployed.appSettings.keys():
        print "Updating app settings"
        client.update_app_settings(container.resourceName, deployed.appName, container.resourceLocation, deployed.appSettings)

    if deployed.connectionName and deployed.connectionValue and deployed.connectionType:
        print "Updating db connection settings"
        client.update_db_conn_settings(container.resourceName, deployed.appName, container.resourceLocation,
                                       deployed.connectionName, deployed.connectionValue, deployed.connectionType)
    print "Done"

if __name__ == '__main__' or __name__ == '__builtin__':
    create_or_update(deployed, deployed.container)
