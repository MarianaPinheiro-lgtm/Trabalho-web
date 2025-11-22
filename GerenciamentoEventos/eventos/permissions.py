from rest_framework import permissions
from django.shortcuts import get_object_or_404
from .models import Perfil, Evento, Inscricao # Ajuste o caminho de importação se necessário

class IsOrganizer(permissions.BasePermission):
    """Permite acesso apenas a usuários que são Organizadores."""
    def has_permission(self, request, view):
        try:
            return request.user.is_authenticated and request.user.perfil.tipo == 'organizador'
        except Perfil.DoesNotExist:
            return False

# permissions.py

from rest_framework import permissions

class IsAlunoOrProfessor(permissions.BasePermission):
    """Permite acesso apenas a usuários que são Alunos ou Professores (Não Organizadores)."""
    message = "Organizadores não têm permissão para se inscrever em eventos."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            perfil = request.user.perfil
            # Retorna True se for 'aluno' ou 'professor'
            return perfil.tipo in ['aluno', 'professor']
        except Exception:
            # Não tem Perfil associado
            return False

class IsOrganizerOrReadOnly(permissions.BasePermission):
    """
    Permite leitura (GET, HEAD, OPTIONS) a todos, 
    mas escrita (POST, PUT, DELETE) apenas a Organizadores.
    """
    def has_permission(self, request, view):
        # Permite GET, HEAD, OPTIONS a todos (Read)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permite escrita apenas se for Organizador
        try:
            return request.user.is_authenticated and request.user.perfil.tipo == 'organizador'
        except Perfil.DoesNotExist:
            return False

class IsResponsibleProfessor(permissions.BasePermission):
    """Permite acesso apenas se o usuário for o Professor responsável pelo Evento."""
    def has_object_permission(self, request, view, obj):
        # Apenas permite acesso se o usuário for o professor do evento (obj é a instância do Evento)
        return obj.professor == request.user

class IsParticipant(permissions.BasePermission):
    """Permite acesso apenas se o usuário for o participante da Inscrição/Certificado."""
    def has_object_permission(self, request, view, obj):
        # obj pode ser Inscricao ou Certificado
        if isinstance(obj, Certificado):
            return obj.inscricao.usuario == request.user
        elif isinstance(obj, Inscricao):
            return obj.usuario == request.user
        return False