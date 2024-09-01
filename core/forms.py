from django import forms
from .models import ProductVersion

class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(min_value=1)
    color = forms.ModelChoiceField(queryset=ProductVersion.objects.none(), required=False)
    storage = forms.ModelChoiceField(queryset=ProductVersion.objects.none(), required=False)

    def __init__(self, *args, **kwargs):
        product = kwargs.pop('product')
        super(AddToCartForm, self).__init__(*args, **kwargs)
        self.fields['color'].queryset = product.colors.all()
        self.fields['storage'].queryset = product.storages.all()

    