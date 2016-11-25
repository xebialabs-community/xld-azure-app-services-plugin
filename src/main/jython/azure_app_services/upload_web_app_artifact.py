from azure_app_services.client import AzureClient
import time

import sys
def upload(deployed, container):
    client = AzureClient.new_instance(container.subscription)
    retry_count = 0
    available = False
    while retry_count < 12:
        print "Checking if Azure ftp upload service available for web site [%s]" % deployed.appName
        rc = client.is_kudu_services_available(deployed.appName)
        if rc == 0:
            available = True
            break
        retry_count += 1
        print "Failed to connect to Azure ftp upload service (rc=%s). Will retry in 5 seconds. Attempt %s" % (rc, retry_count)
        time.sleep(5)

    if not available:
        print "Failed to connect to Azure ftp upload service after 12 attempts. Retry in a while."
        sys.exit(1)

    print "Stopping website if already running. This to prevent file locking."
    client.stop_website(container.resourceName, deployed.appName)

    print "Uploading web site [%s] in resource group [%s]" % (deployed.appName, container.resourceName)
    client.upload_website(deployed.appName, deployed.file.path)

    print "Done"

if __name__ == '__main__' or __name__ == '__builtin__':
    upload(deployed, deployed.container)
