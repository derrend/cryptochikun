import os

chaining = True
client = os.environ.get('CLIENT', 'bitcoin')
client_id = os.environ.get('CLIENT_ID', 'BTC')
vig = 0.02

# these exist for benefit of about.html template
btc_dust_threshold = 0.00000546
ltc_dust_threshold = 0.000546
via_dust_threshold = 0.000546

btc_tx_fee = 0.00075
ltc_tx_fee = 0.001
via_tx_fee = 0.001

btc_min_conf = 2
ltc_min_conf = 3
via_min_conf = 4

def get_minimum_amount(dust_threshold, transaction_fee):
    return round(((dust_threshold / 2) * 100) + transaction_fee, 8)

btc_minimum_amount = get_minimum_amount(btc_dust_threshold, btc_tx_fee)
ltc_minimum_amount = get_minimum_amount(ltc_dust_threshold, ltc_tx_fee)
via_minimum_amount = get_minimum_amount(via_dust_threshold, via_tx_fee)

if client_id in ('BTC',):
    dust_threshold = btc_dust_threshold
    transaction_fee = btc_tx_fee
    minimum_confirmations = btc_min_conf
    minimum_amount = btc_minimum_amount

elif client_id in ('LTC',):
    dust_threshold = ltc_dust_threshold
    transaction_fee = ltc_tx_fee
    minimum_confirmations = ltc_min_conf
    minimum_amount = ltc_minimum_amount

elif client_id in ('VIA',):
    dust_threshold = via_dust_threshold
    transaction_fee = via_tx_fee
    minimum_confirmations = via_min_conf
    minimum_amount = via_minimum_amount

else:
    transaction_fee = False

fastblock_delay = 5  # seconds
