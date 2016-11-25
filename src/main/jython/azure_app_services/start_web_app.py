from azure_app_services.client import AzureClient


def start(deployed, container):
    client = AzureClient.new_instance(container.subscription)
    print "Starting website if already not already running."
    client.start_website(container.resourceName, deployed.appName)
    print "Done"

if __name__ == '__main__' or __name__ == '__builtin__':
    start(deployed, deployed.container)
