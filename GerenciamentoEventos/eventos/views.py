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
from .permissions import IsAlunoOrProfessor
from .models import RegistroAuditoria
from datetime import datetime
from django.shortcuts import get_object_or_404


class RegistroView(FormView):
    template_name = 'registro.html'          # Template onde está o formulário
    form_class = RegistroForm                # Usa o RegistroForm que você criou
    success_url = reverse_lazy('perfil')     # Para onde redirecionar após cadastro

    def form_valid(self, form):
        user = form.save()                   # Salva o usuário e o perfil
        login(self.request, user)            # Faz login automático após cadastro
        
        RegistroAuditoria.objects.create(
            usuario=user, # O próprio usuário que acabou de entrar
            acao="Novo usuário cadastrado no sistema"
        )
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

class EventoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
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
        # 1. Define o organizador (Obrigatório antes de salvar)
        form.instance.organizador = self.request.user
        
        # 2. Salva o evento no banco de dados
        response = super().form_valid(form)
        
        RegistroAuditoria.objects.create(
            usuario=self.request.user,
            acao=f"Criou o evento: {form.instance.nome}"
        )
        return response

class EventoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Evento
    form_class = EventoForm
    template_name = 'evento_form.html'  # mesmo template da criação
    success_url = reverse_lazy('evento_list')  # ou onde quiser redirecionar

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # --- LOG: ALTERAÇÃO DE EVENTO ---
        RegistroAuditoria.objects.create(
            usuario=self.request.user,
            acao=f"Alterou dados do evento: {self.object.nome}"
        )
        return response

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
    
    def form_valid(self, form):
        # Pega o nome antes de deletar para salvar no log
        nome_evento = self.object.nome
        response = super().form_valid(form)
        
        # --- LOG: EXCLUSÃO DE EVENTO ---
        RegistroAuditoria.objects.create(
            usuario=self.request.user,
            acao=f"Excluiu o evento: {nome_evento}"
        )
        return response
    
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

class InscricaoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Inscricao
    form_class = InscricaoForm
    template_name = "inscricao_form.html"
    success_url = reverse_lazy("minhas-inscricoes")

    # 1. Restrição de Organizador
    def test_func(self):
        perfil = getattr(self.request.user, 'perfil', None)
        return perfil and perfil.tipo != 'organizador'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs

    # 2. NOVO: Manda os dados do Evento para o HTML
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pega o ID que veio na URL (definido no urls.py como <int:evento_id>)
        evento_id = self.kwargs.get('evento_id')
        if evento_id:
            # Busca o evento e coloca na variável 'evento' para o HTML usar
            context['evento'] = get_object_or_404(Evento, pk=evento_id)
        return context

    # 3. Salva a inscrição, associa o evento e cria o Log
    def form_valid(self, form):
        try:
            # Pega o evento pelo ID da URL
            evento_id = self.kwargs.get('evento_id')
            evento = get_object_or_404(Evento, pk=evento_id)

            # Preenche os dados automáticos
            form.instance.usuario = self.request.user
            form.instance.evento = evento 

            # Salva no Banco
            response = super().form_valid(form)

            # --- LOG DE AUDITORIA (Requisito de Segurança) ---
            RegistroAuditoria.objects.create(
                usuario=self.request.user,
                acao=f"Inscreveu-se no evento: {evento.nome}"
            )
            # -------------------------------------------------

            return response

        except ValidationError as e:
            form.add_error(None, e.message)
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

        # --- LOG: CONSULTA/GERAÇÃO DE CERTIFICADO ---
        # Só grava o log se o request for GET (visualização)
        # Evita duplicação excessiva, mas garante rastreio
        RegistroAuditoria.objects.create(
            usuario=self.request.user,
            acao=f"Consultou/Gerou certificado do evento: {self.object.evento.nome}"
        )

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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAlunoOrProfessor], throttle_classes = [InscricaoEventosThrottle])
    def inscrever(self, request, pk=None):
        """
        Endpoint: POST /api/eventos/<id>/inscrever/
        Permite que um usuário autenticado se inscreva em um evento.
        """
        evento = self.get_object()
        user = request.user

        #LÓGICA DE VAGAS ADD 
        if evento.vagas_disponiveis is not None and evento.vagas_disponiveis <= 0:
                    return Response({'detail': 'Vagas esgotadas neste evento.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verifica se já está inscrito
        if Inscricao.objects.filter(evento=evento, usuario=user).exists():
            return Response({'detail': 'Você já está inscrito neste evento.'}, status=status.HTTP_400_BAD_REQUEST)

        # Cria inscrição
        inscricao = Inscricao.objects.create(evento=evento, usuario=user)
        RegistroAuditoria.objects.create(
            usuario=user,
            acao=f"Inscreveu-se no evento: {evento.nome}"
        )
        serializer = InscricaoSerializer(inscricao)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # Sobrescreve o método que pega UM evento específico
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # --- LOG: CONSULTA VIA API ---
        if request.user.is_authenticated:
            RegistroAuditoria.objects.create(
                usuario=request.user,
                acao=f"API: Consultou detalhes do evento ID {instance.id} ({instance.nome})"
            )
        # -----------------------------
        
        return super().retrieve(request, *args, **kwargs)

    
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

class AuditoriaListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = RegistroAuditoria
    template_name = 'auditoria_list.html'
    context_object_name = 'registros'
    paginate_by = 20 

    def test_func(self):
        perfil = getattr(self.request.user, 'perfil', None)
        return perfil and perfil.tipo == 'organizador'

    def get_queryset(self):
        # Pega todos os registros ordenados por data (mais recente primeiro)
        qs = RegistroAuditoria.objects.all().order_by('-data_hora')
        
        # --- FILTROS ---
        data_busca = self.request.GET.get('data_busca')
        usuario_busca = self.request.GET.get('usuario_busca')

        # Filtro por Data
        if data_busca:
            try:
                # Converte string 'YYYY-MM-DD' para data e filtra
                data_obj = datetime.strptime(data_busca, '%Y-%m-%d').date()
                qs = qs.filter(data_hora__date=data_obj)
            except ValueError:
                pass # Se a data for inválida, ignora

        # Filtro por Usuário (busca parcial no username)
        if usuario_busca:
            qs = qs.filter(usuario__username__icontains=usuario_busca)
            
        return qs

    # Passa os valores atuais para o template (para o campo não limpar após busca)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_busca'] = self.request.GET.get('data_busca', '')
        context['usuario_busca'] = self.request.GET.get('usuario_busca', '')
        return context