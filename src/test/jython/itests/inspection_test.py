#
# Copyright 2017 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import unittest

from itests import CiStub, SubscriptionCi

from azure_app_services.client import AzureClient

from azure_app_services import inspect


class InspectionContextMock(object):

    def __init__(self):
        self.cis = []

    def discovered(self, ci):
        pass

    def inspected(self, ci):
        self.cis.append(ci)

class DescriptorMock(object):

    def newInstance(self, id):
        ci = CiStub()
        ci.id = id

        if (id.rfind("/") != -1):
            ci.name = id[id.rfind("/")+1:]
        else:
            ci.name = id
        return ci


class InspectionTest(unittest.TestCase):

    def setUp(self):
        self.subscription = SubscriptionCi()
        self.inspection_ctx = InspectionContextMock()
        self.descriptor = DescriptorMock()

    def test_discovery(self):
        self.client = AzureClient.new_instance(self.subscription)
        inspect.perform_discovery(self.subscription, self.inspection_ctx, self.descriptor, self.descriptor)
        for ci in self.inspection_ctx.cis:
            print ci.__dict__
        # self.assertTrue(len(self.inspection_ctx) > 0)

