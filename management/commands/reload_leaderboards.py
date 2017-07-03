from django.core.management.base import BaseCommand, CommandError
from chikun.models import ResultModel, AmountModel, GainsModel, SpreadModel, NarrowModel
from chikun import gvars
from decimal import Decimal

class Command(BaseCommand):
    help = 'Update leaderboards to latest results.'

    def handle(self, *args, **options):
        queryset = ResultModel.objects.all()
        if queryset.exists():

            amount_object = AmountModel.objects.first()
            gains_object = GainsModel.objects.first()
            spread_object = SpreadModel.objects.first()
            narrow_object = NarrowModel.objects.first()
            for i in queryset:

                gains = i.loser_amount - (i.loser_amount * Decimal(gvars.vig))

                if i.winner_amount > amount_object.high_amount:
                    amount_object.high_amount = i.winner_amount
                    amount_object.txid = i.txid
                    amount_object.save()

                if gains > gains_object.high_gains:
                    gains_object.high_gains = gains
                    gains_object.txid = i.txid
                    gains_object.save()

                spread = i.winner_amount - i.loser_amount
                if spread > spread_object.high_spread:
                    spread_object.high_spread = spread
                    spread_object.txid = i.txid
                    spread_object.save()

                if spread < narrow_object.high_narrow or narrow_object.high_narrow == 0:
                    narrow_object.high_narrow = spread
                    narrow_object.txid = i.txid
                    narrow_object.save()
