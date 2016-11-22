from azure_app_services.client import AzureClient


def create_or_update(deployed, container):
    client = AzureClient.new_instance(container.subscription)
    print "Defining app service plan [%s] in resource group [%s]" % (deployed.servicePlanName, container.resourceName)
    client.create_app_service_plan(container.resourceName, deployed.servicePlanName, deployed.location, deployed.sku, deployed.workerSize)
    print "Done"

if __name__ == '__main__' or __name__ == '__builtin__':
    create_or_update(deployed, deployed.container)
