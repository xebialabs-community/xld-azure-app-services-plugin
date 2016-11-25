from azure_app_services.client import AzureClient


def stop(deployed, container):
    client = AzureClient.new_instance(container.subscription)
    print "Stopping website if already running."
    client.stop_continuous_webjob(deployed.webJobName, deployed.appName)
    print "Done"

if __name__ == '__main__' or __name__ == '__builtin__':
    stop(previousDeployed, previousDeployed.container)
