from azure_app_services.client import AzureClient


def create_or_update(deployed, container):
    client = AzureClient.new_instance(container.subscription)
    print "Checking for web application [%s]" % deployed.appName
    if not client.website_exists(container.resourceName, deployed.appName):
        raise Exception("Web application [%s] in resource group [%s] not found" % (deployed.appName, container.resourceName))
    print "Deploying triggered web job [%s] to  web app [%s] in resource group [%s]" % (deployed.webJobName, deployed.appName, container.resourceName)
    client.deploy_triggered_webjob(deployed.webJobName, deployed.appName, deployed.executableFileName, deployed.schedule, deployed.file.path)
    print "Done"

if __name__ == '__main__' or __name__ == '__builtin__':
    create_or_update(deployed, deployed.container)
