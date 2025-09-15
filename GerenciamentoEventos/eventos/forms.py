from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Evento, Inscricao, Perfil, Certificado



class RegistroForm(forms.ModelForm):
    telefone = forms.CharField(max_length=15, required=True)
    instituicao = forms.CharField(max_length=100, required=False)
    tipo = forms.ChoiceField(choices=Perfil.TIPOS[0:2], required=True)

    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput
    )
    password_confirm = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'password']

    def clean_password_confirm(self):
        senha = self.cleaned_data.get("password")
        senha_confirm = self.cleaned_data.get("password_confirm")
        if senha and senha_confirm and senha != senha_confirm:
            raise forms.ValidationError("As senhas não coincidem.")
        return senha_confirm

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            Perfil.objects.create(
                usuario=user,
                telefone=self.cleaned_data['telefone'],
                instituicao=self.cleaned_data['instituicao'],
                tipo=self.cleaned_data['tipo']
            )
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuário",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu usuário'})
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua senha'})
    )

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['nome', 'tipo', 'descricao', 'data_inicio', 'data_fim', 'horario_inicio', 'horario_fim', 'local', 'quantidade_participantes']
class InscricaoForm(forms.ModelForm):
    class Meta:
        model = Inscricao
        fields = ['evento']  # usuário vem da view, não do form
        widgets = {
            'evento': forms.Select(attrs={'class': 'form-control'})
        }
    def _init_(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        super()._init_(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        evento = cleaned_data.get('evento')

        if evento and self.usuario:
            if evento.organizador == self.usuario:
                raise forms.ValidationError("Você não pode se inscrever no seu próprio evento.")

            if Inscricao.objects.filter(usuario=self.usuario, evento=evento).exists():
                raise forms.ValidationError("Você já está inscrito neste evento.")

        return cleaned_data

class CertificadoForm(forms.ModelForm):
    class Meta:
        model = Certificado
        fields = ['inscricao']  # só o necessário
        widgets = {
            'inscricao': forms.Select(attrs={'class': 'form-control'})
        }