
from datetime import datetime
from distutils.util import strtobool
from django.contrib.contenttypes.models import ContentType
from django.core.validators import URLValidator
from django.db.models import F
from django.utils import timezone
from rest_framework import serializers as sz
from transactions.models import Transactions, TransactionType

class TransactionGetSerializer(sz.Serializer):
    # serializer for listing get request
    id = sz.UUIDField()
    parent_id = sz.UUIDField(allow_null=True, source="parent_id.id")
    type = sz.ChoiceField(choices=TransactionType.choices)
    amount = sz.DecimalField(max_digits=20, decimal_places = 2)

class TransactionRequestSerializer(sz.Serializer):
    # Serializes request data payload while creation of transaction
    parent_id = sz.PrimaryKeyRelatedField(queryset=Transactions.objects.all(), allow_null = True, required = False)
    type = sz.ChoiceField(choices=TransactionType.choices)
    amount = sz.DecimalField(max_digits=20, decimal_places = 2)

class TransactionTypeRequestSerializer(sz.Serializer):
    # Serializes request type of transaction
    type = sz.ChoiceField(choices=TransactionType.choices)

class TransactionTypeResponseSerializer(sz.Serializer):
    # Serializes response type of transaction
    id = sz.UUIDField()

