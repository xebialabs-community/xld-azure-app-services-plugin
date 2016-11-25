from azure_app_services.client import AzureClient


def destroy(deployed, container):
    client = AzureClient.new_instance(container.subscription)
    print "Checking for web application [%s]" % deployed.appName
    if not client.website_exists(container.resourceName, deployed.appName):
        print "Web application [%s] in resource group [%s] not found" % (deployed.appName, container.resourceName)
        print "Will not attempt to delete web job as it would have been destroyed with web app"
        return

    print "Deleting continuous web job [%s] from  web app [%s] in resource group [%s]" % (deployed.webJobName, deployed.appName, container.resourceName)
    client.remove_continuous_webjob(deployed.webJobName, deployed.appName)
    print "Done"

if __name__ == '__main__' or __name__ == '__builtin__':
    destroy(previousDeployed, previousDeployed.container)
