from azure_app_services.client import AzureClient
import time


def upload(deployed, container):
    client = AzureClient.new_instance(container.subscription)
    retry_count = 0
    while retry_count < 10:
        print "Checking if Azure ftp upload service available for web site [%s]" % deployed.appName
        service_available = client.is_kudu_services_available(deployed.appName)
        if service_available:
            break
        else:
            retry_count += 1
            print "Failed to connect to Azure ftp upload service. Will retry in 5 seconds. Attempt %s" % retry_count
            time.sleep(5)

    print "Stopping website if already running. This to prevent file locking."
    client.stop_website(container.resourceName, deployed.appName)

    print "Uploading web site [%s] in resource group [%s]" % (deployed.appName, container.resourceName)
    client.upload_website(deployed.appName, deployed.file.path)

    print "Done"

if __name__ == '__main__' or __name__ == '__builtin__':
    upload(deployed, deployed.container)
