from django import forms


class RFIDSaleForm(forms.Form):
    rfid = forms.CharField(label='RFID', max_length=100)
