from django import forms

from budget.models import Category
from core.mixins.forms import BootstrapFormMixin


class CategoryForm(forms.ModelForm, BootstrapFormMixin):
    class Meta:
        model = Category
        fields = ('name', 'category_type', 'icon')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_bootstrap()
