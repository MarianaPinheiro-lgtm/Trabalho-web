def perfil_context(request):
    if request.user.is_authenticated:
        return {'perfil': getattr(request.user, 'perfil', None)}
    return {}