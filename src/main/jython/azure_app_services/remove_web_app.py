from azure_app_services.client import AzureClient


def destroy(deployed, container):
    client = AzureClient.new_instance(container.subscription)
    print "Destroying web site [%s] from resource group [%s]" % (deployed.appName, container.resourceName)
    found = client.destroy_website(container.resourceName, deployed.appName)
    if not found:
        print "Web site was not found. Destroy operation ignored."
    print "Done"

if __name__ == '__main__' or __name__ == '__builtin__':
    destroy(previousDeployed, previousDeployed.container)
