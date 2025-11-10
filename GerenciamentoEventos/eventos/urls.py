from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventoViewSet
from . import views

router = DefaultRouter()
router.register(r'eventos', EventoViewSet, basename='evento')

urlpatterns = [
    path('', include(router.urls)),
    path('inscricoes/', views.InscricaoListView.as_view(), name='api_inscricoes_list'),
    path('eventos/', views.EventoListView.as_view(), name='api_eventos_list'),
    path('eventos/<int:pk>/', views.EventoUpdateView.as_view(), name='api_evento_detail'),
    path('inscricoes/criar/', views.InscricaoCreateView.as_view(), name='api_inscricao_create'),
    
]