from django import forms

from service.models import Services


class ServiceForm(forms.ModelForm):

    class Meta:
        model = Services
        fields = ['service_name', 'description', 'price', 'duration', 'status']
        widgets = {
            'service_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Hair Cut'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'price': 'Price (₹)',
            'duration': 'Duration (minutes)',
        }

    def clean_service_name(self):
        name = self.cleaned_data['service_name'].strip()
        if len(name) < 3:
            raise forms.ValidationError('Service name must have at least 3 characters.')

        qs = Services.objects.filter(service_name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('A service with this name already exists.')
        return name

    def clean_price(self):
        price = self.cleaned_data['price']
        if price is not None and price <= 0:
            raise forms.ValidationError('Price must be greater than 0.')
        return price

    def clean_duration(self):
        duration = self.cleaned_data['duration']
        if duration is not None:
            if duration <= 0:
                raise forms.ValidationError('Duration must be at least 1 minute.')
            if duration > 1440:
                raise forms.ValidationError('Duration cannot be more than 1440 minutes (24 hours).')
        return duration
