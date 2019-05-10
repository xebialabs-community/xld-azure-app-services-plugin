#
# Copyright 2019 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

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
