"""
URL configuration for GerenciamentoEventos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.contrib.auth.views import LogoutView, LoginView
from eventos.views import (
    RegistroView,  
    PerfilView,
    EventoCreateView,
    EventoUpdateView,
    EventoDeleteView,
    EventoListView,
    EventoListView2,
    InscricaoCreateView,
    InscricaoListView,
    CertificadoView
)
urlpatterns = [
    path('admin/', admin.site.urls),
      # Autenticação
    path('registro/', RegistroView.as_view(), name='registro'),
    path('', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    # Perfil
    path('perfil/', PerfilView.as_view(), name='perfil'),

    # Eventos
    path('evento/listas/', EventoListView.as_view(), name='evento_list'),
    path('evento/listas2/', EventoListView2.as_view(), name='evento_list2'),
    path('evento/criar/', EventoCreateView.as_view(), name='evento_create'),
    path('evento/<int:pk>/editar/', EventoUpdateView.as_view(), name='evento_update'),
    path('evento/<int:pk>/excluir/', EventoDeleteView.as_view(), name='evento_delete'),

    # Inscrições
    path('inscricao/criar/', InscricaoCreateView.as_view(), name='inscricao_create'),
    path('inscricoes/', InscricaoListView.as_view(), name='minhas-inscricoes'),
    # Certificado
    path('certificado/<int:pk>/', CertificadoView.as_view(), name='certificado'),

]