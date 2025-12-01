## Integrantes: Hugo Martins, João Marcos, Mariana Pinheiro 

# Sistema de Gerenciamento de Eventos Acadêmicos:

## Uma aplicação web para cadastrar, alterar, excluir, visualizar e acessar eventos acadêmicos. Desenvolvido para alunos, professores e organizadores dos eventos. 

## Objetivos: 

O objetivo desse projeto é aplicar os conceitos de desenvolvimento web com Django, explorando: 

* Criação de modelos (models) e migrações 

* Utilização do Django Admin 

* Criação de rotas e views 

* Templates com HTML e CSS 

* Integração com banco de dados SQLite 

## Funcionalidades: 

 * Cadastro de usuários (Aluno, Professor, Organizador) 

 * Cadastro de eventos (: tipo de evento, data de início e fim, horário, local, capacidade de participantes e organizador responsável) 

 * Inscrição de usuários em eventos 

 * Emissão de certificados 

 * Autenticação de usuários 

## Tecnologias Utilizadas:

  1. Python 
  2. Django 5.2.7 
  3. SQLite3 
  4. HTML5 / CSS3 
  5. Visual Studio Code 
  6. Git e GitHub 

## Estrutura do Projeto: 
```
  GerenciamentoEventos/ 
  ├── eventos/ 
  │ ├── migrations/ 
  │ ├── templates/ 
  │ │ ├── base.html/ 
  │ │ ├── baseSemLogin.html 
  │ │ ├── baseSemLoginSair.html 
  │ │ ├── certificado.html 
  │ │ ├── evento_confirm_delete.html 
  │ │ ├── evento_form.html 
  │ │ ├── evento_list.html 
  │ │ ├── evento_list2.html 
  │ │ ├── inscricao_form.html 
  │ │ ├── inscricao_list.html 
  │ │ ├── perfil.html 
  │ │ └── registro.html 
  │ ├── admin.py 
  │ ├── models.py 
  │ ├── views.py 
  │ ├── apps.py 
  │ ├── tests.py 
  │ └── forms.py 
  ├── GerenciamentoEventos/ 
  │ ├── settings.py 
  │ ├── asgi.py 
  │ ├── urls.py 
  │ └── wsgi.py 
  ├── db.sqlite3 
  ├── manage.py 
  └── README.md
```

## Como Executar o Projeto: 

	1- Clonar repositório: 
	Utilize, por meio do git bash, o comando: git clone (“url do repositório”). E em seguida o comando: cd Trabalho-web. Para acessar a pasta do projeto. 

	2- Criar e ativar um ambiente virtual: 
	Para Windows, utilize os comandos, na pasta do projeto: python -m venv venv. E 	após: venv\Scripts\activate  
	Já para Linux: python3 -m venv venv. E após: source venv/bin/activate  

	3- Instalando o Django: 
	Utilize, dentro da pasta venv, por meio do cmd, o comando: pip install django. 	Para instalar o Django. 

	4- Executar migrações: 
	Utilize o comando “python manage.py migrate” para realizar as migrações. 

	5-Rodar servidor: 
	Utiliza o comando “python manage.py runserver” para rodar o servidor. 

	6- Acessar o sistema: 
	Acesse o sistema pelo IP e porta recomendados pelo Django, após o comando 	de rodar o servidor. 
