from azure_app_services.client import AzureClient


def check_connection(subscription):
    client = AzureClient.new_instance(subscription)
    print "Checking connection by fetching known resource groups."
    print client.list_resource_groups()
    print "Done"

if __name__ == '__main__' or __name__ == '__builtin__':
    check_connection(thisCi)
