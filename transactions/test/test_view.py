from multiprocessing import context
import re
from transactions.test.tests import BaseTestCase
import pytest
from transactions.models import Transactions, TransactionType
from django.urls import reverse
from deepdiff import DeepDiff
from django.db import connection
from django.http import Http404
from transactions.serializers import TransactionGetSerializer, TransactionRequestSerializer, TransactionTypeRequestSerializer, TransactionTypeResponseSerializer
import json

class TestTransactionListView(BaseTestCase):
    @pytest.fixture
    def transaction_fixtures_list(self):
        """
        Fixture to create dummy Transaction instances to be used in tests
        """
        for i in range(5):
            Transactions.objects.create(
                type=TransactionType.shopping, amount=500+i*10
            )

    @pytest.mark.usefixtures("transaction_fixtures_list")
    def test_get_all_transactions(self, *args):
        """
        Tests fetching all existing transactions
        """
        uri = reverse('transaction-list-post')
        resp = self.client.get(uri)
        resp_body = resp.json()
        assert resp.status_code == 200
        transaction_objects = Transactions.objects.all()
        response = TransactionGetSerializer(
            transaction_objects, many=True
        ).data
        
        assert not DeepDiff(resp_body, json.loads(json.dumps(response)), ignore_order=True)

    def test_create_transactions_without_parentid(self, *args, **kwargs):
        """
        Tests creation of a new transaction where parent id is None
        """
        uri = reverse('transaction-list-post')
        req_data = {
            "type": TransactionType.shopping,
            "amount": 200,
        }
        resp = self.client.post(uri, data=req_data)
        resp_content = resp.json()
        assert resp.status_code == 201
        assert not DeepDiff(resp_content, "New transaction is created", ignore_order=True)

    @pytest.mark.usefixtures("transaction_fixtures_list")
    def test_create_transactions_valid_parentid(self, *args, **kwargs):
        """
        Tests creation of a new transaction with valid parent id
        """
        uri = reverse('transaction-list-post')
        parent_transaction = Transactions.objects.first()
        req_data = {
            "parent_id":parent_transaction.id,
            "type": TransactionType.shopping,
            "amount": 200,
        }
        resp = self.client.post(uri, data=req_data)
        resp_content = resp.json()
        assert resp.status_code == 201
        assert not DeepDiff(resp_content, "New transaction is created", ignore_order=True)
    def test_create_transactions_invalid_parentid(self, *args, **kwargs):
        """
        Tests creation of a new transaction with invalid parent id
        """
        uri = reverse('transaction-list-post')
        req_data = {
            "parent_id":"1324",
            "type": TransactionType.shopping,
            "amount": 200,
        }
        resp = self.client.post(uri, data=req_data)
        resp_content = resp.json()
        assert resp.status_code == 400
        assert not DeepDiff(resp_content, {f'parent_id': ['Invalid pk "1324" - object does not exist.']}, ignore_order=True)

    @pytest.mark.usefixtures("transaction_fixtures_list")
    def test_create_transactions_invalid_type(self, *args, **kwargs):
        """
        Tests creation of a new transaction with invalid type
        """
        uri = reverse('transaction-list-post')
        parent_transaction = Transactions.objects.first()
        req_data = {
            "parent_id":parent_transaction.id,
            "type": "invalid-type",
            "amount": 200,
        }
        resp = self.client.post(uri, data=req_data)
        resp_content = resp.json()
        assert resp.status_code == 400
        assert not DeepDiff(resp_content, {'type': ['"invalid-type" is not a valid choice.']}, ignore_order=True)

    @pytest.mark.usefixtures("transaction_fixtures_list")
    def test_create_transactions_without_type(self, *args, **kwargs):
        """
        Tests creation of a new transaction with without type
        """
        uri = reverse('transaction-list-post')
        parent_transaction = Transactions.objects.first()
        req_data = {
            "parent_id":parent_transaction.id,
            "amount": 200,
        }
        resp = self.client.post(uri, data=req_data)
        resp_content = resp.json()
        assert resp.status_code == 400
        assert not DeepDiff(resp_content, {'type': ['This field is required.']}, ignore_order=True)

    @pytest.mark.usefixtures("transaction_fixtures_list")
    def test_create_transactions_invalid_amount(self, *args, **kwargs):
        """
        Tests creation of a new transaction with invalid amount
        """
        uri = reverse('transaction-list-post')
        parent_transaction = Transactions.objects.first()
        req_data = {
            "parent_id":parent_transaction.id,
            "type": TransactionType.shopping,
            "amount": "invalid-amount",
        }
        resp = self.client.post(uri, data=req_data)
        resp_content = resp.json()
        assert resp.status_code == 400
        assert not DeepDiff(resp_content, {'amount': ['A valid number is required.']}, ignore_order=True)

    @pytest.mark.usefixtures("transaction_fixtures_list")
    def test_create_transactions_without_amount(self, *args, **kwargs):
        """
        Tests creation of a new transaction with without amount
        """
        uri = reverse('transaction-list-post')
        parent_transaction = Transactions.objects.first()
        req_data = {
            "parent_id":parent_transaction.id,
            "type": TransactionType.shopping,
        }
        resp = self.client.post(uri, data=req_data)
        resp_content = resp.json()
        assert resp.status_code == 400
        assert not DeepDiff(resp_content, {'amount': ['This field is required.']}, ignore_order=True)

class TestTransactionDetailView(BaseTestCase):
    @pytest.fixture
    def transaction_fixtures_list(self):
        """
        Fixture to create dummy Transaction instances to be used in tests
        """
        Transactions.objects.create(
                type=TransactionType.shopping, amount=300
            )
        transaction = Transactions.objects.all()[0]
        Transactions.objects.create(
                parent_id=transaction,type=TransactionType.shopping, amount=200
            )

    @pytest.mark.usefixtures("transaction_fixtures_list")
    def test_get_single_transaction_valid_id(self, *args):
        """
        Tests fetching a single transaction with valid id
        """
        transaction = Transactions.objects.all()[0]
        uri = reverse('transaction-detail', kwargs={'pk':transaction.id })
        resp = self.client.get(uri)
        resp_body = resp.json()
        assert resp.status_code == 200
        transaction_object=Transactions.objects.get(pk = resp_body["id"])
        response=TransactionGetSerializer(
            transaction_object
        ).data
        assert not DeepDiff(resp_body, json.loads(json.dumps(response)), ignore_order=True)

    def test_get_single_transaction_invalid_id(self, *args):
        """
        Tests fetching a single transaction with invalid id
        """
        uri = reverse('transaction-detail', kwargs={'pk':"123" })
        resp = self.client.get(uri)
        resp_body = resp.json()
        assert resp.status_code == 404

    @pytest.mark.usefixtures("transaction_fixtures_list")
    def test_update_transactions_with_valid_data(self, *args, **kwargs):
        """
        Tests updation of a transaction when request body is valid
        """
        transaction = Transactions.objects.first()
        uri = reverse('transaction-detail', kwargs={'pk':transaction.id })
        req_data = {
            "parent_id": Transactions.objects.all()[1].id,
            "type": TransactionType.shopping,
            "amount": 250,
        }
        resp = self.client.put(uri, data=req_data, content_type='application/json')
        resp_content = resp.json()
        num_updates=Transactions.objects.filter(pk = transaction.id).update(**req_data)
        assert not DeepDiff(resp_content, f"{num_updates} Transaction details updated", ignore_order=True)

    def test_update_transactions_invalid_parentid(self, *args, **kwargs):
        """
        Tests updation of a transaction with invalid parent id
        """
        uri = reverse('transaction-list-post')
        req_data = {
            "parent_id":"1324",
            "type": TransactionType.shopping,
            "amount": 200,
        }
        resp = self.client.post(uri, data=req_data)
        resp_content = resp.json()
        assert resp.status_code == 400
        assert not DeepDiff(resp_content, {f'parent_id': ['Invalid pk "1324" - object does not exist.']}, ignore_order=True)

    @pytest.mark.usefixtures("transaction_fixtures_list")
    def test_update_transactions_invalid_type(self, *args, **kwargs):
        """
        Tests updation of transaction with invalid type
        """
        uri = reverse('transaction-list-post')
        parent_transaction = Transactions.objects.first()
        req_data = {
            "parent_id":parent_transaction.id,
            "type": "invalid-type",
            "amount": 200,
        }
        resp = self.client.post(uri, data=req_data)
        resp_content = resp.json()
        assert resp.status_code == 400
        assert not DeepDiff(resp_content, {'type': ['"invalid-type" is not a valid choice.']}, ignore_order=True)

    @pytest.mark.usefixtures("transaction_fixtures_list")
    def test_update_transactions_invalid_amount(self, *args, **kwargs):
        """
        Tests updatio of transaction with invalid amount
        """
        uri = reverse('transaction-list-post')
        parent_transaction = Transactions.objects.first()
        req_data = {
            "parent_id":parent_transaction.id,
            "type": TransactionType.shopping,
            "amount": "invalid-amount",
        }
        resp = self.client.post(uri, data=req_data)
        resp_content = resp.json()
        assert resp.status_code == 400
        assert not DeepDiff(resp_content, {'amount': ['A valid number is required.']}, ignore_order=True)

class TestTransactionTypeView(BaseTestCase):
    @pytest.fixture
    def transaction_fixtures_list(self):
        """
        Fixture to create dummy Transaction instances to be used in tests
        """
        Transactions.objects.create(
                type=TransactionType.shopping, amount=300
            )
        transaction = Transactions.objects.first()
        Transactions.objects.create(
                parent_id=transaction,type=TransactionType.shopping, amount=200
            )

    @pytest.mark.usefixtures("transaction_fixtures_list")
    def test_get_transactions_valid_type(self, *args):
        """
        Tests fetching a single transactions with valid type
        """
        uri = reverse('transaction-type', kwargs={'type':"shopping" })
        resp = self.client.get(uri)
        resp_body = resp.json()
        assert resp.status_code == 200
        types = Transactions.objects.filter(type = "shopping")
        response = TransactionTypeResponseSerializer(
            types, many=True
        ).data
        assert not DeepDiff(resp_body, json.loads(json.dumps(response)), ignore_order=True)

    def test_get_transactions_invalid_type(self, *args):
        """
        Tests fetching a single transaction with invalid type
        """
        uri = reverse('transaction-type', kwargs={'type':"invalid-type" })
        resp = self.client.get(uri)
        resp_body = resp.json()
        assert resp.status_code == 400
        assert resp_body=={'type': ['"invalid-type" is not a valid choice.']}


class TestTransactionSumView(BaseTestCase):
    @pytest.fixture
    def transaction_fixtures_skewed_tree(self):
        """
        Fixture to create dummy Transaction instances to be used in tests

        300(a)---> 200(b) ---> 100(c)
        """
        transaction_first = Transactions.objects.create(
                type=TransactionType.shopping, amount=300
            )
        transaction_second = Transactions.objects.create(
                parent_id=transaction_first,type=TransactionType.shopping, amount=200
            )
        transaction_third = Transactions.objects.create(
            parent_id=transaction_second,type=TransactionType.shopping, amount=100
        )

    @pytest.fixture
    def transaction_fixtures_binary_tree(self):
        """
        Fixture to create dummy Transaction instances to be used in tests
        """
                #            300(a)
                #             /  \
                #            /    \
                #       (b)200    (c)100
                #          /\       /\
                #         /  \     /  \
                #    10(d)  20(e) 30(f)40(g) 
        
        transaction_first = Transactions.objects.create(
                type=TransactionType.shopping, amount=300
            )
        transaction_first_left = Transactions.objects.create(
                parent_id=transaction_first,type=TransactionType.shopping, amount=200
            )
        transaction_first_right = Transactions.objects.create(
            parent_id=transaction_first,type=TransactionType.shopping, amount=100
        )
        Transactions.objects.create(
                parent_id=transaction_first_left,type=TransactionType.shopping, amount=10
            )
        Transactions.objects.create(
            parent_id=transaction_first_left,type=TransactionType.shopping, amount=20
        )
        Transactions.objects.create(
                parent_id=transaction_first_right,type=TransactionType.shopping, amount=30
            )
        Transactions.objects.create(
            parent_id=transaction_first_right,type=TransactionType.shopping, amount=40
        )
        
    def get_transaction_amount(self, pk):
        with connection.cursor() as cursor:
            cursor.execute("with recursive cte as (select id as input_id, id, amount from transactions_transactions t where id = %s union all select cte.input_id, tc.id, tc.amount from cte join transactions_transactions tc on tc.parent_id_id = cte.id) select sum(amount) from cte group by input_id",[pk])
            row = cursor.fetchone()
            return row[0] if row else 0

    @pytest.mark.usefixtures("transaction_fixtures_skewed_tree")
    def test_sum_of_transactions_valid_parentid_skewed_tree(self, *args, **kwargs):
        """
        Tests sum of all amounts startng from node(a) as parent id from following example
           start--> 300(a)---> 200(b) ---> 100(c)
        """
        transaction = Transactions.objects.get(parent_id = None)
        uri = reverse('transaction-sum', kwargs={'pk':transaction.id })
        resp = self.client.get(uri)
        resp_content = resp.json()
        transaction_amt = self.get_transaction_amount(transaction.id)
        assert resp_content["sum"]==600
        assert not DeepDiff(resp_content,{"sum":float(transaction_amt)} , ignore_order=True)
        
    @pytest.mark.usefixtures("transaction_fixtures_skewed_tree")
    def test_sum_of_transactions_invalid_parentid(self, *args, **kwargs):
        """
        Tests sum of all nested amounts of given invalid parent id
        """
        uri = reverse('transaction-sum', kwargs={'pk':"1-2-3" })
        resp = self.client.get(uri)
        resp_content = resp.json()
        assert resp.status_code == 200
        assert resp_content=={'sum': 0}

    @pytest.mark.usefixtures("transaction_fixtures_binary_tree")
    def test_sum_of_transactions_valid_parentid_binary_tree(self, *args, **kwargs):
        """
        Tests sum of all amounts startng from node(a) as parent id from following example
        """
                #     start-->300(a)
                #             /  \
                #            /    \
                #       (b)200    (c)100
                #          /\       /\
                #         /  \     /  \
                #    10(d)  20(e) 30(f)40(g) 
        transaction = Transactions.objects.get(parent_id = None)
        uri = reverse('transaction-sum', kwargs={'pk':transaction.id })
        resp = self.client.get(uri)
        resp_content = resp.json()
        transaction_amt = self.get_transaction_amount(transaction.id)
        assert resp_content["sum"]==700
        assert not DeepDiff(resp_content,{"sum":float(transaction_amt)} , ignore_order=True)

    @pytest.mark.usefixtures("transaction_fixtures_binary_tree")
    def test_sum_of_transactions_valid_parentid_binary_tree(self, *args, **kwargs):
        """
        Tests sum of all amounts startng from node(b) as parent id from following example
        """
                #            300(a)
                #             /  \
                #            /    \
                #start-->(b)200    (c)100
                #          /\       /\
                #         /  \     /  \
                #    10(d)  20(e) 30(f)40(g) 
        transaction = Transactions.objects.get(amount = 200)
        uri = reverse('transaction-sum', kwargs={'pk':transaction.id })
        resp = self.client.get(uri)
        resp_content = resp.json()
        transaction_amt = self.get_transaction_amount(transaction.id)
        assert resp_content["sum"]==230
        assert not DeepDiff(resp_content,{"sum":float(transaction_amt)} , ignore_order=True)
        





