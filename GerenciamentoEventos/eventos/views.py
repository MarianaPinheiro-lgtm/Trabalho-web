from django.shortcuts import render
from django.shortcuts import render
from django.shortcuts import render
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib.auth import login
from .forms import RegistroForm, LoginForm, EventoForm, InscricaoForm
from django.contrib.auth.views import LoginView as AuthLoginView
from django.views.generic import TemplateView, CreateView,  UpdateView, DeleteView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Perfil, Evento, Inscricao, Certificado
from django.core.exceptions import ValidationError
from django.contrib import messages
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Evento, Inscricao
from .serializers import EventoSerializer, InscricaoSerializer
from .throttles import ConsultaEventosThrottle, InscricaoEventosThrottle
from django.core.mail import send_mail
from django.http import HttpResponse



class RegistroView(FormView):
    template_name = 'registro.html'          # Template onde está o formulário
    form_class = RegistroForm                # Usa o RegistroForm que você criou
    success_url = reverse_lazy('perfil')     # Para onde redirecionar após cadastro

    def form_valid(self, form):
        user = form.save()                   # Salva o usuário e o perfil
        login(self.request, user)            # Faz login automático após cadastro
        return super().form_valid(form)

class LoginView(AuthLoginView):
    template_name = 'login.html'          # O template do formulário de login
    authentication_form = LoginForm       # O formulário que você criou
    redirect_authenticated_user = True    # Redireciona se já estiver logado
    success_url = reverse_lazy('perfil')  # Para onde vai após login com sucesso
class PerfilView(LoginRequiredMixin, TemplateView):
    template_name = 'perfil.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        perfil = Perfil.objects.get(usuario=usuario)
        context['usuario'] = usuario
        context['perfil'] = perfil
        return context

class EventoCreateView(LoginRequiredMixin, CreateView):
    model = Evento
    form_class = EventoForm
    template_name = 'evento_form.html'
    success_url = reverse_lazy('evento_list')  # ou outro nome de view
    login_url = 'login'  # Redireciona se não estiver logado
    def test_func(self):
        # Só organizadores podem criar eventos
        perfil = getattr(self.request.user, 'perfil', None)
        return perfil and perfil.tipo == 'organizador'

    def form_valid(self, form):
        form.instance.organizador = self.request.user  # Define o organizador como o usuário logado
        return super().form_valid(form)
class EventoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Evento
    form_class = EventoForm
    template_name = 'evento_form.html'  # mesmo template da criação
    success_url = reverse_lazy('evento_list')  # ou onde quiser redirecionar

    def form_valid(self, form):
        form.instance.organizador = self.request.user  # mantém o organizador
        return super().form_valid(form)

    def test_func(self):
        evento = self.get_object()
        return self.request.user == evento.organizador  # só o organizador pode editar
class EventoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Evento
    template_name = 'evento_confirm_delete.html'
    success_url = reverse_lazy('evento_list')  # Para onde redirecionar após excluir

    def test_func(self):
        evento = self.get_object()
        return self.request.user == evento.organizador  # só o organizador pode excluir
        
class EventoListView(ListView):
    model = Evento
    template_name = 'evento_list.html'  # Caminho para o template
    context_object_name = 'eventos'     # Nome da variável usada no template
    ordering = ['data_inicio']          # Ordena os eventos por data de início

class EventoListView2(ListView):
    model = Evento
    template_name = 'evento_list2.html'  # Caminho para o template
    context_object_name = 'eventos'     # Nome da variável usada no template
    ordering = ['data_inicio']          # Ordena os eventos por data de início

class InscricaoCreateView(CreateView):
    model = Inscricao
    form_class = InscricaoForm
    template_name = "inscricao_form.html"
    success_url = reverse_lazy("minhas-inscricoes")  # redireciona após salvar
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user  # passa o usuário para o formulário
        return kwargs
    def form_valid(self, form):
 # associa automaticamente o usuário logado
        form.instance.usuario = self.request.user
        try:
            return super().form_valid(form)
        except ValidationError as e:
            form.add_error(None, e.message)  # mostra o erro no HTML
            return self.form_invalid(form)
class InscricaoListView(ListView):
    model = Inscricao
    template_name = "inscricao_list.html"
    context_object_name = "inscricoes"

    def get_queryset(self):
        # mostra só as inscrições do usuário logado
        return Inscricao.objects.filter(usuario=self.request.user)
    


class CertificadoView(DetailView):
    model = Inscricao
    template_name = "certificado.html"
    context_object_name = "inscricao"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Garante que o usuário só veja o próprio certificado
        if self.object.usuario != self.request.user:
            raise PermissionError("Você não tem permissão para ver este certificado.")

        # Cria o certificado se não existir
        certificado, created = Certificado.objects.get_or_create(inscricao=self.object)

        context['certificado'] = certificado
        return context
# Create your views here.

#API 06/11 08:52

class EventoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint de leitura: lista e detalha eventos
    """
    queryset = Evento.objects.all().order_by('data_inicio')
    serializer_class = EventoSerializer
    throttle_classes = [ConsultaEventosThrottle]
    
    def get_queryset(self):
        # Filter articles to only show those belonging to the current user
        print("Deu certo!")
        return Evento.objects.all().order_by('data_inicio')

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], throttle_classes = [InscricaoEventosThrottle])
    def inscrever(self, request, pk=None):
        """
        Endpoint: POST /api/eventos/<id>/inscrever/
        Permite que um usuário autenticado se inscreva em um evento.
        """
        evento = self.get_object()
        user = request.user

        # Verifica se já está inscrito
        if Inscricao.objects.filter(evento=evento, usuario=user).exists():
            return Response({'detail': 'Você já está inscrito neste evento.'}, status=status.HTTP_400_BAD_REQUEST)

        # Cria inscrição
        inscricao = Inscricao.objects.create(evento=evento, usuario=user)
        serializer = InscricaoSerializer(inscricao)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
#inscricoes API

class InscricaoViewSet(viewsets.ModelViewSet):
    queryset = Inscricao.objects.all()
    serializer_class = InscricaoSerializer
    Permission_classes = [IsAuthenticated]
    throttle_classes = [InscricaoEventosThrottle]

#envio de email

def teste_email(request):
    send_mail(
        'Testando envio',
        'Este é um email de teste enviado pelo Django.',
        'hugo.martins@sempreceub.com',
        ['joao.loliveira@sempreceub.com'],  # pode enviar para você mesmo
    )
    return HttpResponse("E-mail enviado!")