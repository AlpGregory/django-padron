from django.urls import path

from . import views
from .views import LoginView, NewVoterView, DeleteVoterView

urlpatterns = [
    path('votantes/', views.voters, name='voters'),
    path('votantes/<str:pk>/', views.voter_info, name='voter_info'),
    path('login/', LoginView.as_view(
         template_name='votes/login.html',
         redirect_authenticated_user=True),
         name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('gestion-votantes/agregar/', NewVoterView.as_view(
         template_name='votes/new_voter.html'),
         name='new_voter'),
    path('gestion-votantes/eliminar/<str:pk>', DeleteVoterView.as_view(), name='delete_voter')
]
