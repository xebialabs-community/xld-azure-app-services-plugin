import unittest
from itests import SubscriptionCi
from azure_app_services import check_connection


class CheckConnectionTest(unittest.TestCase):

    def test_connection(self):
        check_connection.check_connection(SubscriptionCi())




