import django_tables2 as tables
from models import ResultModel, AmountModel, GainsModel, SpreadModel, NarrowModel
from gvars import client_id

# TODO probably a better way to do this but it will do for now.
block_explorer_url = 'https://blockchain.info/tx/'
if not client_id == 'BTC':
    block_explorer_url = 'https://chainz.cryptoid.info/{}/tx.dws?'.format(client_id.lower())

class ResultTable(tables.Table):
    class Meta:
        model = ResultModel
        # add class="paleblue" to <table> tag
        attrs = {'class': 'paleblue'}
        #fields = ['winner_address']

    txid = tables.TemplateColumn('<a href="%s{{record.txid}}" target="_blank">{{record.txid}}</a>' % block_explorer_url)

class AmountTable(tables.Table):
    class Meta:
        model = AmountModel
        attrs = {'class': 'paleblue'}

    high_amount = tables.TemplateColumn('<a href="%s{{record.txid}}" target="_blank">{{record.high_amount}}</a>' % block_explorer_url)

class GainsTable(tables.Table):
    class Meta:
        model = GainsModel
        attrs = {'class': 'paleblue', 'exclude': 'id'}

    high_gains = tables.TemplateColumn('<a href="%s{{record.txid}}" target="_blank">{{record.high_gains}}</a>' % block_explorer_url)

class SpreadTable(tables.Table):
    class Meta:
        model = SpreadModel
        attrs = {'class': 'paleblue'}

    high_spread = tables.TemplateColumn('<a href="%s{{record.txid}}" target="_blank">{{record.high_spread}}</a>' % block_explorer_url)

class NarrowTable(tables.Table):
    class Meta:
        model = NarrowModel
        attrs = {'class': 'paleblue'}

    high_narrow = tables.TemplateColumn('<a href="%s{{record.txid}}" target="_blank">{{record.high_narrow}}</a>' % block_explorer_url)
