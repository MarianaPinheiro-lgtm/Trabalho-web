from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventoViewSet
from . import views

# --- Configuração da API (JSON) ---
router = DefaultRouter()
router.register(r'eventos', EventoViewSet, basename='api-evento') 
# Dica: Usei 'api-evento' no basename para diferenciar dos nomes das urls do site

urlpatterns = [
    
    # Lista de Eventos (HTML)
    path('eventos/', views.EventoListView.as_view(), name='evento_list'),
    
    # Detalhes/Edição de Evento (HTML)
    path('eventos/<int:pk>/', views.EventoUpdateView.as_view(), name='evento_detail'),
    
    # Lista de Inscrições (HTML)
    path('inscricoes/', views.InscricaoListView.as_view(), name='inscricao_list'),
    
    # Criar Inscrição (HTML)
    path('inscricoes/criar/', views.InscricaoCreateView.as_view(), name='inscricao_create'),

    # Auditoria (HTML - Adicionei conforme conversamos antes)
    path('auditoria/', views.AuditoriaListView.as_view(), name='auditoria_list'),


    # =========================================
    # 🤖 ROTAS DA API (JSON / Mobile)
    # =========================================
    # Todas as rotas do router ficarão acessíveis em: /api/eventos/
    
    path('api/', include(router.urls)),
]