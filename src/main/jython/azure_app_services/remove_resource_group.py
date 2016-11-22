from azure_app_services.client import AzureClient


def destroy(rg):
    client = AzureClient.new_instance(rg.subscription)
    print "Destroying resource group [%s]" % rg.resourceName
    found = client.destroy_resource_group(rg.resourceName)
    if not found:
        print "Resource group was not found. Destroy operation ignored."
    print "Done"

if __name__ == '__main__' or __name__ == '__builtin__':
    destroy(thisCi)
