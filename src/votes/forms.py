from django import forms
from votes.models import Person, Location


class SearchLocationForm(forms.Form):
    """
    A class for the searching form in /voters/ page

    ...

    Attributes
    ----------
    identification : CharField
        legal voter identification
    name : CharField
        the name of the voter
    """
    identification = forms.CharField(label='identification', max_length=20, required=False)
    name = forms.CharField(label='name', max_length=100, required=False)


class NewVoterForm(forms.ModelForm):
    """
    A class for the new voter information

    ...

    Attributes
    ----------
    identification : IntegerField
        legal voter identification as numbers
    elec_code : ModelChoiceField
        voter's electoral location
    full_name : CharField
        voter's full name
    id_expiration_date : DateField
        date of voter id's expiration
    """
    identification = forms.IntegerField(label='Identificación', required=True, widget=forms.NumberInput(
        attrs={'class': 'form-control me-2',
               'type': 'search',
               'aria-label': 'Search'}))

    elec_code = forms.ModelChoiceField(label='Lugar de votación', queryset=Location.objects.all(), widget=forms.Select(
        attrs={'class': 'form-control me-2',
               'type': 'search'}))

    full_name = forms.CharField(label='Nombre', required=True, widget=forms.TextInput(
        attrs=({'class': 'form-control me-2',
                'type': 'search',
                'aria-label': 'Search'})))

    id_expiration_date = forms.DateField(label='Fecha de vencimiento de la cédula', required=True,
                                         widget=forms.SelectDateWidget(
                                             attrs={'class': 'form-control me-2',
                                                    'type': 'search',
                                                    'aria-label': 'Search'}))

    class Meta:
        model = Person
        fields = ['identification', 'elec_code',
                  'full_name', 'id_expiration_date']
