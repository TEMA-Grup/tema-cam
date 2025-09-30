from django import forms

class SelectTenantForm(forms.Form):
    tenant = forms.ChoiceField(label="Şirket", choices=[])

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop("choices", [])
        super().__init__(*args, **kwargs)
        self.fields["tenant"].choices = choices
