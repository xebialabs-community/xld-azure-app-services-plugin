from azure_app_services.client import AzureClient


def destroy(deployed, container):
    client = AzureClient.new_instance(container.subscription)
    print "Destroying app service plan [%s] from resource group [%s]" % (deployed.servicePlanName, container.resourceName)
    found = client.destroy_app_service_plan(container.resourceName, deployed.servicePlanName)
    if not found:
        print "App service plan was not found. Destroy operation ignored."
    print "Done"

if __name__ == '__main__' or __name__ == '__builtin__':
    destroy(previousDeployed, previousDeployed.container)
