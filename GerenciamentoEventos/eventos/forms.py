from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Evento, Inscricao, Perfil, Certificado



class RegistroForm(forms.ModelForm):
    telefone = forms.CharField(
        max_length=15, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone','id':'telefone','name':'telefone'})
    )
    instituicao = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Instituição'})
    )
    tipo = forms.ChoiceField(
        choices=Perfil.TIPOS,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua senha'})
    )
    password_confirm = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirme sua senha'})
    )
    class Meta: 
        model = User
        fields = ['username', 'first_name', 'email', 'password']
        help_texts= {'username': None} 

    email = forms.EmailField(required=True)

    def clean_password_confirm(self):
        senha = self.cleaned_data.get("password") 
        senha_confirm = self.cleaned_data.get("password_confirm") 
        if senha and senha_confirm and senha != senha_confirm: 
            raise forms.ValidationError("As senhas não coincidem.") 
        return senha_confirm 
    
    def save(self, commit=True): 
        user = super().save(commit=False) 
        user.set_password(self.cleaned_data["password"]) 
        if commit: user.save() 
        Perfil.objects.create( usuario=user, telefone=self.cleaned_data['telefone'], instituicao=self.cleaned_data['instituicao'], tipo=self.cleaned_data['tipo'] ) 
        return user

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("E-mail já cadastrado. Use outro endereço.")
        return email
    
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
        fields = [
            'nome', 'tipo', 'descricao',
            'data_inicio', 'data_fim',
            'horario_inicio', 'horario_fim',
            'local', 'quantidade_participantes','banner','professor'
        ]
        widgets = {
            'data_inicio': forms.DateInput(
                format='%d/%m/%Y',
                attrs={'class': 'form-control', 'placeholder': 'dd/mm/aaaa'}
            ),
            'data_fim': forms.DateInput(
                format='%d/%m/%Y',
                attrs={'class': 'form-control', 'placeholder': 'dd/mm/aaaa'}
            ),
            'horario_inicio': forms.TimeInput(
                format='%H:%M',
                attrs={'class': 'form-control', 'placeholder': 'hh:mm'}
            ),
            'horario_fim': forms.TimeInput(
                format='%H:%M',
                attrs={'class': 'form-control', 'placeholder': 'hh:mm'}
            ),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'local': forms.TextInput(attrs={'class': 'form-control'}),
            'quantidade_participantes': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_inicio'].input_formats = ['%d/%m/%Y']
        self.fields['data_fim'].input_formats = ['%d/%m/%Y']
        self.fields['horario_inicio'].input_formats = ['%H:%M']
        self.fields['horario_fim'].input_formats = ['%H:%M']
        self.fields['professor'].queryset = User.objects.filter(perfil__tipo='professor')
    def clean_banner(self):
        banner = self.cleaned_data.get('banner')
        if banner:
            if not banner.content_type.startswith('image/'):
                raise forms.ValidationError("O arquivo deve ser uma imagem (jpg, png, etc).")
            if banner.size > 5*1024*1024:  # limite de 5MB
                raise forms.ValidationError("A imagem não pode ter mais de 5MB.")
        return banner

class InscricaoForm(forms.ModelForm):
    class Meta:
        model = Inscricao
        fields = ['evento']  # usuário vem da view, não do form
        widgets = {
            'evento': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

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