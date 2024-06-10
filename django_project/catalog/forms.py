from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User, Department, InsurancePolicy, Contract

class RegistrationForm(UserCreationForm):
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'last_name', 'first_name', 'middle_name', 'email', 'address', 'phone_number', 'age', 'department', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.status != 'agent':
            self.fields['department'].widget = forms.HiddenInput()
        else:
            self.fields['department'].required = True

class InsurancePolicyForm(forms.ModelForm):
    class Meta:
        model = InsurancePolicy
        fields = ['policy_number', 'agent', 'contract', 'start_date', 'end_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contract'].queryset = Contract.objects.filter(insurancepolicy__isnull=True)

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['department', 'insurance_type', 'insurable_object', 'insurance_risk', 'insurance_amount', 'promo_code']

class ContractSearchForm(forms.Form):
    client = forms.CharField(label='Клиент', required=False)
