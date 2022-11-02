from django.test import TestCase
from django.test import TransactionTestCase, Client, RequestFactory
from django.core import management
import pytest

class BaseTestCase(TransactionTestCase):
    # fixtures = ["data/fixtures/test_dummy_data.json"]

    DEFAULT_CONTENT_TYPE = 'application/json'

    # Loads fixture file data in theBaseTestCase DB so that the data is available to other custom fixtures
    # @pytest.fixture
    # def load_test_fixtures_data(self):
    #     management.call_command('loaddata', self.fixtures[0], verbosity=0)

    def setUp(self) -> None:
        super(BaseTestCase, self).setUp()
        self.factory = RequestFactory()
        self.client = Client()

