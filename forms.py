from django import forms
from captcha.fields import CaptchaField
from models import AddressModel

class CaptchaTestForm(forms.Form):
    captcha = CaptchaField()

class AddressForm(forms.ModelForm):
    class Meta:
        model = AddressModel
        fields = ["return_address"]

class SearchForm(forms.Form):
    search = forms.CharField(label='Search ID, Address, Amount or Txid')
