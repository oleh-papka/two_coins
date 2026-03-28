from django import forms

from budget.models import Category
from core.mixins.forms import BootstrapFormMixin


class CategoryForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'category_type', 'icon', 'color')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_bootstrap()


class ReservedCategoryUpdateForm(CategoryForm):
    class Meta:
        model = Category
        fields = ('icon', 'color')
