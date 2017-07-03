from django.shortcuts import render, render_to_response, HttpResponse, redirect
from django.template.context_processors import csrf
from django.core.exceptions import ValidationError
from subprocess import Popen, PIPE
from models import AddressModel, ResultModel, AmountModel, GainsModel, SpreadModel, NarrowModel
from forms import CaptchaTestForm, AddressForm, SearchForm
from pycoin.key.validate import is_address_valid
import json
import gvars
from graphos.renderers.gchart import LineChart
from graphos.sources.model import ModelDataSource
from tables import ResultTable, AmountTable, GainsTable, SpreadTable, NarrowTable
from django_tables2 import RequestConfig
import logging

# # Process imports
# import sys
# import random
# import os

logging.basicConfig(filename='views.log', level=logging.DEBUG, format='%(asctime)s %(message)s')
#chaining = True  #TODO put this in gvars?
general_error_message = 'Something bad happened.'

# Create your views here.
def deposit(request):
    if request.method == "GET":
        html_dict = dict(form_capcha=CaptchaTestForm(),
                         form_address=AddressForm(),
                         current=request.path,
                         client_id=gvars.client_id.lower())

        unspent = []
        try:
            unspent = json.loads(Popen([
                'coin-cli',
                '-rpcconnect={}_coind'.format(gvars.client_id.lower()),
                'listunspent',
                '0'
            ],
                stdout=PIPE).communicate()[0])

            unspent_filtered = []
            for i in unspent:
                if i.get('amount') >= gvars.minimum_amount:
                    unspent_filtered.append(i)

        except ValueError:
            #unspent_filtered = []  #TODO move this before try?
            logging.debug('ValueError in deposit.get 0 view.\nIs the coin daemon active?')
            request.session['error_message'] = general_error_message
        except OSError:
            #unspent_filtered = []  #TODO move this before try?
            logging.debug('OSError in deposit.get 0 view.\nIs the coin daemon installed?')
            request.session['error_message'] = general_error_message

        error_message = request.session.get('error_message', False)
        if error_message:
            html_dict.update(error_message=error_message)
            del request.session['error_message']

        html_dict.update(count=len(unspent_filtered))

        html_dict.update(csrf(request))
        return render_to_response('deposit_get.html', html_dict)
    if request.method == 'POST':
        form = CaptchaTestForm(request.POST)

        # check valid capcha
        if not form.is_valid():
            request.session['error_message'] = 'Invalid captcha.'
            return redirect('deposit')

        # check valid address
        if not is_address_valid(request.POST['return_address']) == gvars.client_id:
            request.session['error_message'] = 'Invalid {} return address.'.format(gvars.client.title())
            return redirect('deposit')

        # placed before internal address check on purpose
        try:
            deposit_address = Popen([
                'coin-cli',
                '-rpcconnect={}_coind'.format(gvars.client_id.lower()),
                "getnewaddress"
            ],
                stdout=PIPE).communicate()[0].strip()
        except ValueError:
            logging.debug('ValueError in deposit.post 0 view.\nIs the coin daemon active?')
            request.session['error_message'] = general_error_message

        # allow chaining
        if not gvars.chaining:
            try:
                internal_address_list = json.loads(Popen([
                    'coin-cli',
                    '-rpcconnect={}_coind'.format(gvars.client_id.lower()),
                    'getaddressesbyaccount',
                    ""
                ],
                    stdout=PIPE).communicate()[0])
            except ValueError:
                logging.debug('ValueError in deposit.post 1 view.\nIs the coin daemon active?')
                request.session['error_message'] = general_error_message

            if request.POST['return_address'] in internal_address_list:
                request.session['error_message'] = 'Chain betting is disabled'
                return redirect('deposit')

        # create address model
        AddressModel.objects.create(deposit_address=deposit_address,
                                    return_address=request.POST['return_address']
                                    ).save()

        html_dict = dict(deposit_address=deposit_address,
                         minimum_amount=gvars.minimum_amount,
                         client_id=gvars.client_id,
                         client=gvars.client,
                         current=request.path)

        return render_to_response('deposit_post.html', html_dict)

def results(request):
    queryset = ResultModel.objects.none()

    if request.method == "POST":
        # TODO Make more efficient.
        query = request.POST.get('search')
        queryset = ResultModel.objects.filter(winner_address=query) |\
                   ResultModel.objects.filter(loser_address=query) |\
                   ResultModel.objects.filter(txid=query)

        if not queryset.exists():
            try:
                queryset = ResultModel.objects.filter(winner_amount=query) |\
                           ResultModel.objects.filter(loser_amount=query)
            except ValidationError:
                logging.debug('ValidationError in results.post 0 view.')
                request.session['error_message'] = general_error_message

        if not queryset.exists():
            request.session['error_message'] = 'No matching records.'

    if not queryset.exists():
        queryset = ResultModel.objects.all()

    if not queryset.exists():
        request.session['error_message'] = 'No results yet.'
        return redirect('deposit')

    queryset = queryset.order_by('-id')
    form = SearchForm()
    chart = ModelDataSource(queryset[:100], fields=['id', 'winner_amount', 'loser_amount'])
    chart = LineChart(chart, options=dict(title='100 History',
                                          curveType='function',
                                          animation=dict(duration=1000,
                                                         startup=True,
                                                         easing='out')))
                                          # series={0: dict(labelInLegend='Winning Amount'),
                                          #         1: dict(labelInLegend='Losing Amount')}))

    result_table = ResultTable(queryset)
    RequestConfig(request, paginate=dict(per_page=100)).configure(result_table)

    amount_table = AmountTable(AmountModel.objects.all()[:1])
    gains_table = GainsTable(GainsModel.objects.all()[:1])
    spread_table = SpreadTable(SpreadModel.objects.all()[:1])
    narrow_table = NarrowTable(NarrowModel.objects.all()[:1])
    # amount_table = AmountTable(AmountModel.objects.all().order_by('-high_amount')[:1])
    # gains_table = GainsTable(GainsModel.objects.all().order_by('-high_gains')[:1])
    # spread_table = SpreadTable(SpreadModel.objects.all().order_by('-high_spread')[:1])
    # narrow_table = NarrowTable(NarrowModel.objects.all().order_by('-high_narrow')[:1])
    # amount_table = AmountTable(AmountModel.objects.last())
    # gains_table = GainsTable(GainsModel.objects.last())
    # spread_table = SpreadTable(SpreadModel.objects.last())
    # narrow_table = NarrowTable(NarrowModel.objects.last())
    for i in (amount_table, gains_table, spread_table, narrow_table):
        i.exclude = ('id', 'txid')
        RequestConfig(request, paginate=dict(per_page=1)).configure(i)

    html_dict = dict(current=request.path,
                     form=form,
                     chart=chart,
                     result_table=result_table,
                     amount_table=amount_table,
                     gains_table=gains_table,
                     spread_table=spread_table,
                     narrow_table=narrow_table)

    error_message = request.session.get('error_message', False)
    if error_message:
        html_dict.update(error_message=error_message)
        del request.session['error_message']

    html_dict.update(csrf(request))
    return render(request, 'results.html', html_dict)

def about(request):
    if request.method == "GET":
        html_dict = dict(minimum_confirmations=gvars.minimum_confirmations - 1,
                         gvars=gvars,
                         vig=gvars.vig * 100,  # can't multiply in template without installing additional software.
                         current=request.path)

        return render_to_response('about.html', html_dict)
