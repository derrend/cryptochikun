from __future__ import unicode_literals
from django.db import models
from django.core.validators import MaxValueValidator

# Create your models here.
class AddressModel(models.Model):
    deposit_address = models.CharField(verbose_name='Return Address:', max_length=34, blank=False, null=False, editable=False)
    return_address = models.CharField(verbose_name='Return Address:', max_length=34, blank=False, null=False, editable=True)

class ResultModel(models.Model):
    winner_address = models.CharField(verbose_name="Winning Address", max_length=34, null=False, blank=False)
    winner_amount = models.DecimalField(verbose_name="Winning Amount", max_digits=16, decimal_places=8, editable=False, validators=[MaxValueValidator(21000000)])
    loser_amount = models.DecimalField(verbose_name="Losing Amount", max_digits=16, decimal_places=8, editable=False, validators=[MaxValueValidator(21000000)])
    loser_address = models.CharField(verbose_name="Losing Address", max_length=34, null=False, blank=False)
    txid = models.CharField(verbose_name="Txid", max_length=64, null=False, blank=False)

class AmountModel(models.Model):
    high_amount = models.DecimalField(default=0, verbose_name="Highest Wager", max_digits=16, decimal_places=8, editable=False,
                                        validators=[MaxValueValidator(21000000)])
    txid = models.CharField(default=None, verbose_name="Txid", max_length=64, null=True, blank=False)

class GainsModel(models.Model):
    high_gains = models.DecimalField(default=0, verbose_name="Largest Gains", max_digits=16, decimal_places=8, editable=False,
                                        validators=[MaxValueValidator(21000000)])
    txid = models.CharField(default=None, verbose_name="Txid", max_length=64, null=True, blank=False)

class SpreadModel(models.Model):
    high_spread = models.DecimalField(default=0, verbose_name="Widest Spread", max_digits=16, decimal_places=8, editable=False,
                                        validators=[MaxValueValidator(21000000)])
    txid = models.CharField(default=None, verbose_name="Txid", max_length=64, null=True, blank=False)

class NarrowModel(models.Model):
    high_narrow = models.DecimalField(default=0, verbose_name="Narrowest Spread", max_digits=16, decimal_places=8, editable=False,
                                        validators=[MaxValueValidator(21000000)])
    txid = models.CharField(default=None, verbose_name="Txid", max_length=64, null=True, blank=False)
