#!/usr/bin/python
from django.core.management.base import BaseCommand, CommandError
from chikun.models import AddressModel, ResultModel, AmountModel, GainsModel, SpreadModel, NarrowModel
from subprocess import Popen, PIPE
import random
import json
import os
import sys
from chikun import gvars
import logging
from django.core.cache import cache as rdb
from redis.exceptions import ConnectionError
from django.db.utils import OperationalError

logging.basicConfig(filename='process.log', level=logging.DEBUG, format='%(asctime)s %(message)s')
# activate nonessential logging
LOGON = True
#LOGON = False

# TODO move this to gvars?
# if gvars.client_id == 'BTC':
#     comission_address = '1PzbWgkJvCo3bnD6kwEbeZK1dCSheYgdT'
# elif gvars.client_id == 'LTC':
#     comission_address = 'LZj8p5xDFCap557NJtZNGDhpqtdivve4bn'

# check redis cache is running
try:
    # abort if minimum time delay between blocks is not met
    if rdb.get('{}_fastblock'):
        logging.debug('{} fastblock detected, process function aborted.'.format(gvars.client_id))
        rdb.expire('{}_fastblock', timeout=gvars.fastblock_delay)
        sys.exit()
    rdb.set('{}_fastblock', True, timeout=gvars.fastblock_delay)
except ConnectionError:
    logging.debug('{} redis cache not responding. Is it running?'.format(gvars.client_id))
    sys.exit()

comission_address = os.environ.get('COMISSION_ADDRESS')
if not comission_address:
    logging.debug('{} Comission address returned FALSE.'.format(gvars.client_id))
    sys.exit()

if not gvars.transaction_fee:
    logging.debug('{} transaction fee returned FALSE.'.format(gvars.client_id))
    sys.exit()

class Command(BaseCommand):
    help = 'Calculate results and initiate payment'

    def handle(self, *args, **options):
        try:
            unspent = json.loads(Popen([
                'coin-cli',
                # '-rpcconnect={}_coind'.format(gvars.client_id.lower()),
                'listunspent',
                str(gvars.minimum_confirmations)
            ],
                stdout=PIPE).communicate()[0])
        except ValueError:
            logging.debug('{} ValueError in process.command.handle 0 view.\nIs the coin daemon active?'.format(gvars.client_id))
            sys.exit()
        except OSError:
            logging.debug('{} OSError in process.command.handle 0 view.\nIs the coin daemon installed?'.format(gvars.client_id))
            sys.exit()
        except UnboundLocalError:
            logging.debug('{} local variable \'unspent\' referenced before assignment'.format(gvars.client_id))
            sys.exit()


        # filter minimum amount deposits
        unspent_filtered = []
        for i in unspent:
            if LOGON:
                logging.debug('{} input amount {}'.format(gvars.client_id, i.get('amount')))  # testing
            if i.get('amount') >= gvars.minimum_amount:
                unspent_filtered.append(i)
        if LOGON:
            logging.debug('{} minimum amount {}'.format(gvars.client_id, gvars.minimum_amount))  # testing

        if len(unspent_filtered) < 2:
            if LOGON:
                logging.debug('{} not enough inputs in unspent_filtered list ({})'.format(gvars.client_id, len(unspent_filtered)))  # testing
            sys.exit()

        random.shuffle(unspent_filtered)
        pairs = zip(unspent_filtered[::2], unspent_filtered[1::2])
        for i in pairs:

            # do not execute if address or amount are the same
            if not i[0].get('address') == i[1].get('address') and not i[0].get('amount') == i[1].get('amount'):
                winner, loser = (i[0], i[1]) if i[0].get('amount') > i[1].get('amount') else (i[1], i[0])
                chikun_amount = round((loser.get('amount') - gvars.transaction_fee) * gvars.vig, 8)
                #chikun_amount = round(loser.get('amount') * gvars.vig, 8)
                #gains = round(((loser.get('amount') - (gvars.transaction_fee * 2)) - chikun_amount) - gvars.transaction_fee, 8)
                gains = round((loser.get('amount') - gvars.transaction_fee) - chikun_amount, 8)
                # check postgres db is running
                try:
                    return_address = AddressModel.objects.filter(deposit_address=winner.get('address'))[0].return_address
                except OperationalError:
                    logging.debug('{} postgres db not responding. Is it running?'.format(gvars.client_id))
                    sys.exit()
                # return_address = 'LcynbFy2mPK2cyFVqzjwPM5MfU6wGubBrc'  # testing

                # create raw transaction
                try:
                    raw_transaction = Popen([
                        'coin-cli',
                        # '-rpcconnect={}_coind'.format(gvars.client_id.lower()),
                        'createrawtransaction',
                        json.dumps([
                            dict(txid=winner.get('txid'), vout=winner.get('vout')),
                            dict(txid=loser.get('txid'), vout=loser.get('vout'))
                        ]),
                        json.dumps({
                            return_address: round(winner.get('amount') + gains, 8),
                            comission_address: chikun_amount
                        })
                    ],
                        stdout=PIPE).communicate()[0].strip()
                except ValueError:
                    logging.debug('{} ValueError in process.command.handle 1 view.\nIs the coin daemon active?'.format(gvars.client_id))
                    sys.exit()

                # sign raw transaction
                try:
                    signed_transaction = json.loads(Popen([
                        'coin-cli',
                        # '-rpcconnect={}_coind'.format(gvars.client_id.lower()),
                        'signrawtransaction',
                        raw_transaction
                    ],
                        stdout=PIPE).communicate()[0])['hex'].strip()
                except ValueError:
                    logging.debug('{} ValueError in process.command.handle 2 view.\nIs the coin daemon active?'.format(gvars.client_id))
                    sys.exit()
                if LOGON:
                    logging.debug('{} Raw tx:\n{}'.format(gvars.client_id, raw_transaction))  # testing
                    logging.debug('{} Signed tx:\n{}'.format(gvars.client_id, signed_transaction))  # testing

                # broadcast raw transaction
                try:
                    txid = Popen([
                        'coin-cli',
                        # '-rpcconnect={}_coind'.format(gvars.client_id.lower()),
                        'sendrawtransaction',
                        signed_transaction
                    ], stdout=PIPE).communicate()[0].strip()
                except ValueError:
                    logging.debug('{} ValueError in process.command.handle 3 view.\nIs the coin daemon active?'.format(gvars.client_id))
                    sys.exit()
                # txid = '672fe6b846f9bc5c0fe16ad15eed8ccd48a51a0be623cdc49e8ad4ff6d0b0760'  # testing

                # create result model
                ResultModel.objects.create(winner_address=winner.get('address'),
                                           winner_amount=winner.get('amount'),
                                           loser_address=loser.get('address'),
                                           loser_amount=loser.get('amount'),
                                           txid=txid
                                           ).save()

                for ii in (AmountModel, GainsModel, SpreadModel, NarrowModel):
                    if not ii.objects.all().exists():
                        ii.objects.create().save()

                if len(AmountModel.objects.all()) > 1:
                    AmountModel.objects.all().order_by('-high_amount')[:1]

                queryobject = AmountModel.objects.first()
                if LOGON:
                    logging.debug('{} Winner amount {}\nHigh amount {}'.format(gvars.client_id, winner.get('amount'), queryobject.high_amount))  # testing
                if winner.get('amount') > queryobject.high_amount:
                    queryobject.high_amount = winner.get('amount')
                    queryobject.txid = txid
                    queryobject.save()

                queryobject = GainsModel.objects.first()
                if LOGON:
                    logging.debug('{} Gains {}\nHigh gains {}'.format(gvars.client_id, gains, queryobject.high_gains))  # testing
                if gains > queryobject.high_gains:
                    queryobject.high_gains = gains
                    queryobject.txid = txid
                    queryobject.save()

                spread = winner.get('amount') - loser.get('amount')
                queryobject = SpreadModel.objects.first()
                if LOGON:
                    logging.debug('{} Spread {}\nHigh spread {}'.format(gvars.client_id, spread, queryobject.high_spread))  # testing
                if spread > queryobject.high_spread:
                    queryobject.high_spread = spread
                    queryobject.txid = txid
                    queryobject.save()

                queryobject = NarrowModel.objects.first()
                if LOGON:
                    logging.debug('{} Spread {}\nHigh_narrow {}'.format(gvars.client_id, spread, queryobject.high_narrow))  # testing
                if spread < queryobject.high_narrow or queryobject.high_narrow == 0:
                    queryobject.high_narrow = spread
                    queryobject.txid = txid
                    queryobject.save()
