from email.policy import default
from pyexpat import model
from unicodedata import decimal
from django.db import models
import uuid
from django.db import OperationalError
from django.utils.translation import gettext_lazy as _
import datetime
from django.utils import timezone


# Create your models here.

class BaseModel(models.Model):
    id = models.CharField(default = uuid.uuid4, primary_key=True, max_length=36)
    # to track when the current document was created on
    created_on = models.DateTimeField(default = timezone.now())
    # to track when the current record was last modified on
    modified_on = models.DateTimeField(auto_now=True)

    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        if self.is_deleted:
            raise OperationalError(f'Object does not exist, it has already been soft-deleted')
        # update the is_deleted flag; to mark it archived
        self.is_deleted = True
        self.save(*args, **kwargs)  # Call the save() method

class TransactionType(models.TextChoices):
    shopping = 'shopping', _('shopping')
    fuel = 'fuel', _('fuel')
    house_hold = 'house_hold', _('house_hold')

class Transactions(BaseModel):
    parent_id = models.ForeignKey('Transactions', on_delete = models.SET_NULL, null = True, default=None)
    type = models.CharField(max_length=50, choices=TransactionType.choices)
    amount = models.DecimalField(max_digits=20, decimal_places = 2)

