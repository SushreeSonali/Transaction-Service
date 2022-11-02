from urllib import response
from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.db import connection
from transactions.models import Transactions
from transactions.serializers import TransactionGetSerializer, TransactionRequestSerializer, TransactionTypeRequestSerializer, TransactionTypeResponseSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class TransactionList(APIView):
    """
    List all transactions, or create a new Transaction.
    """
    def get(self, request, format=None):
        """List all transactions"""
        transaction_objects = Transactions.objects.all()
        response = TransactionGetSerializer(
            transaction_objects, many=True
        ).data
        return Response(response)

    def post(self, request):
        """Create a new Transaction"""
        serializer = TransactionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        Transactions.objects.create(**data)
        return Response("New transaction is created", status=status.HTTP_201_CREATED)


class TransactionDetail(APIView):
    """
    Retrieve or update Transaction instance.
    """
    def get_object(self, pk):
        try:
            return Transactions.objects.get(pk=pk)
        except :
            raise Http404

    def get(self, request, pk, format=None):
        """Get details of input transaction"""
        transaction_object = self.get_object(pk)
        response = TransactionGetSerializer(
            transaction_object
        ).data
        return Response(response)

    def put(self, request, pk, format=None):
        """ update details of input transaction"""
        serializer = TransactionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        num_updates=Transactions.objects.filter(pk = pk).update(**data)
        return Response(f"{num_updates} Transaction details updated")

class TransactionTypeView(APIView):
    def get(self, request, type, format=None):
        serializer = TransactionTypeRequestSerializer(data={"type":type})
        serializer.is_valid(raise_exception=True)
        serializer.validated_data
        types = Transactions.objects.filter(type = type)
        response = TransactionTypeResponseSerializer(
            types, many=True
        ).data
        return Response(response)

class TransactionSum(APIView):
    def get_transaction_amount(self, pk):
        with connection.cursor() as cursor:
            cursor.execute("with recursive cte as (select id as input_id, id, amount from transactions_transactions t where id = %s union all select cte.input_id, tc.id, tc.amount from cte join transactions_transactions tc on tc.parent_id_id = cte.id) select sum(amount) from cte group by input_id",[pk])
            row = cursor.fetchone()
            return row[0] if row else 0
        
    def get(self, request, pk, format=None):
        transaction_amt = self.get_transaction_amount(pk)
        total_sum = {"sum":transaction_amt}
        return Response(total_sum)
