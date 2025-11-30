from django.db import models
from django.db import models
from django.contrib.auth.models import User


from django.core.exceptions import ValidationError

class Perfil(models.Model):
    TIPOS = [
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
        ('organizador', 'Organizador'),
    ]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    telefone = models.CharField(max_length=15, blank=True)
    instituicao = models.CharField(max_length=255, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    codigo_acesso = models.CharField(max_length=6, blank=True, null=True)
    confirmado = models.BooleanField(default=False)

    def clean(self):
        if self.tipo in ['aluno', 'professor'] and not self.instituicao:
            raise ValidationError("Alunos e Professores precisam informar a instituição.")

    def __str__(self):
        return f"{self.usuario.username} - {self.tipo}"

class Evento(models.Model):
    TIPOS = [
        ('seminario', 'Seminário'),
        ('palestra', 'Palestra'),
        ('workshop', 'Workshop'),
        ('curso', 'Curso'),
    ]
    nome = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    descricao = models.TextField()
    data_inicio = models.DateField()
    data_fim = models.DateField()
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()
    local = models.CharField(max_length=255)
    quantidade_participantes = models.PositiveIntegerField(null=True, blank=True)
    organizador = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="eventos_organizados"
    )
    professor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    banner = models.ImageField(upload_to='banners/', blank=True, null=True)  

    def __str__(self):
        return f"{self.nome} - {self.tipo}"
    @property
    def vagas_disponiveis(self):
        """Retorna número de vagas restantes (se houver limite)."""
        if self.quantidade_participantes:
            return self.quantidade_participantes - self.inscricoes.count()
        return None
class Inscricao(models.Model):
    STATUS = [
        ('inscrito', 'Inscrito'),
        ('cancelado', 'Cancelado'),
        ('presente', 'Presente'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="inscricoes"
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="inscricoes"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='inscrito'
    )
    data_inscricao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'evento')  # Impede inscrição duplicada
        verbose_name = "Inscrição"
        verbose_name_plural = "Inscrições"

    def __str__(self):
        return f"{self.usuario.username} → {self.evento.nome} ({self.status})"
    def save(self, *args, **kwargs):
     if self.evento.quantidade_participantes and self.evento.inscricoes.count() >= self.evento.quantidade_participantes:
        raise ValidationError("Limite de participantes atingido!")
     super(Inscricao, self).save(*args, **kwargs)  # ou super().save(*args, **kwargs)


class Certificado(models.Model):
    inscricao = models.OneToOneField(Inscricao, on_delete=models.CASCADE)
    data_emissao = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"Certificado de {self.inscricao.usuario.username} - {self.inscricao.evento.nome}"


#Auditoria
class RegistroAuditoria(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    acao = models.CharField(max_length=255)
    data_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_hora']

    def __str__(self):
        return f"{self.usuario} - {self.acao} em {self.data_hora}"