#
# Copyright 2017 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

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
