from rest_framework import serializers

from .models import Evento, Inscricao

class EventoSerializer(serializers.ModelSerializer):
    organizador = serializers.StringRelatedField()  # mostra o nome do organizador (User)

    class Meta:
        model = Evento
        fields = ['id', 'nome', 'data', 'local', 'organizador']


class InscricaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inscricao
        fields = ['id', 'evento', 'usuario', 'data_inscricao']
        read_only_fields = ['data_inscricao']