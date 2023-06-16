from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView
from .forms import SearchLocationForm
from .models import Person
from votes.utils import set_database
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import NewVoterForm


DATABASE = set_database()


def voters(request):
    """
    The voters view

    :param request: for html requests
    :return: the same view with the list of voters (if possible)
    """
    param_dict = {}

    if request.method == 'POST':
        form = SearchLocationForm(request.POST)

        if form.is_valid():
            identification = form.cleaned_data['identification']
            name = form.cleaned_data['name']

            voters_info_list = DATABASE.search_voters(identification=identification, name=name.upper())

            param_dict['voters_info_list'] = voters_info_list

    if request.user.is_authenticated:
        param_dict['logout'] = "Cerrar Sesión"

    return render(request, "votes/voters.html", param_dict)


def voter_info(request, pk):
    """
    The voter info view

    :param request: for html requests
    :param voter_id: the voter identification taken from the list
    :return: a view with voter info and some statistics related
    """
    param_dict = {}
    person = DATABASE.get_voter(pk)

    if person is not None:
        elec_code = person.elec_code
        statistics_list = DATABASE.get_voter_statistics(person.id_expiration_date, elec_code)

        param_dict['voter_info_list'] = [person]
        param_dict['statistics_list'] = statistics_list

    else:
        param_dict['error_message'] = 'Voter not found. Make sure the voter already exists.'

    if request.user.is_authenticated:
        param_dict['logout'] = "Cerrar Sesión"

    return render(request, "votes/voter_info.html", param_dict)


class UserLoginView(LoginView):
    """
    A user login view using Django's LoginView
    """
    redirect_authenticated_user = True


@login_required
def logout_view(request):
    """
    The view after the user logs out

    :param request: for html request
    :return: a view of logout message and redirection page
    """
    logout(request)
    return render(request, "votes/logout_view.html")


@method_decorator(login_required, name='dispatch')
class NewVoterView(CreateView):
    """
    A view with the form for new voters
    """
    model = Person
    form_class = NewVoterForm

    def form_valid(self, form):
        self.object = DATABASE.add_voter(form.cleaned_data)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('voter_info', kwargs={'pk': self.object})


@method_decorator(login_required, name='dispatch')
class DeleteVoterView(DeleteView):
    """
    A view to delete voters from database
    """
    model = Person

    def get_object(self, queryset=None):
        return DATABASE.get_voter(self.kwargs.get("pk"))

    def form_valid(self, form):
        success_url = self.get_success_url()
        DATABASE.delete_voter(self.object.pk)
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        return reverse('voters')
