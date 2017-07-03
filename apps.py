from __future__ import unicode_literals

from django.apps import AppConfig
# from models import AmountModel, WinningsModel, SpreadModel
from decimal import Decimal

class ChikunConfig(AppConfig):
    name = 'chikun'
    verbose_name = "crypto-chikun"

    # def ready(self):

        # MyModel = self.get_model('AmountModel')
        # print MyModel
        # if not MyModel.objects.all().exists():
        #     MyModel.objects.create(high_amount=Decimal('0')).save()

        # if not WinningsModel.objects.all().exists():
        #     WinningsModel.objects.create(high_winnings=Decimal('0')).save()
        #
        # if not SpreadModel.objects.all().exists():
        #     SpreadModel.objects.create(high_spread=Decimal('0')).save()
