from django import forms

from store.models import Brand


class CartItemForm(forms.Form):
    quantity = forms.IntegerField(min_value=1)


class ProductFilterForm(forms.Form):
    brand = forms.ModelMultipleChoiceField(
        queryset=Brand.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )