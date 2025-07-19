from django import forms
from .models import CustomUser
from shops.models import Shop

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = CustomUser
        fields = ['phone_number', 'password', 'role', 'first_name', 'last_name', 'shop']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['role'].choices = [(role, role.title()) for role in user.allowed_roles_to_create()]
            if user.role == 'store_admin' and user.shop:
                self.fields['shop'].queryset = Shop.objects.filter(id=user.shop.id)
                self.fields['shop'].initial = user.shop
                self.fields['shop'].disabled = True
            else:
                self.fields['shop'].queryset = Shop.objects.all()
        else:
            self.fields['role'].choices = []  # Default to empty if no user
            self.fields['shop'].queryset = Shop.objects.all()

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("A user with this phone number already exists.")
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        shop = cleaned_data.get('shop')
        user = getattr(self, 'user', None)  # Use getattr to safely access user
        if user and user.role == 'store_admin' and shop and user.shop != shop:
            raise forms.ValidationError("You can only assign users to your own shop.")
        if user and role and role not in user.allowed_roles_to_create():
            raise forms.ValidationError(f"Invalid role selected. Allowed roles: {', '.join(user.allowed_roles_to_create())}.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_staff = (self.cleaned_data['role'] in ['tracky_admin', 'store_admin'])
        if commit:
            user.save()
        return user