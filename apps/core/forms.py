from django import forms

class SelectCompanyForm(forms.Form):
    company = forms.ChoiceField(label = "Şirket", choices=[])

    def __init__(self, *args, **kwargs):
        companies = kwargs.pop("companies", [])
        super().__init__(*args, **kwargs)
        self.fields["company"].choices = [(c.slug, c.name) for c in companies]