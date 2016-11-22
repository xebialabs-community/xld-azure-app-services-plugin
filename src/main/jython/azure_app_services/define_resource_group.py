from azure_app_services.client import AzureClient


def create_or_update(rg):
    client = AzureClient.new_instance(rg.subscription)
    print "Defining resource group [%s] in location [%s]" % (rg.resourceName, rg.resourceLocation)
    client.create_resource_group(rg.resourceName, rg.resourceLocation, rg.resourceTags)
    print "Done"

if __name__ == '__main__' or __name__ == '__builtin__':
    create_or_update(thisCi)
