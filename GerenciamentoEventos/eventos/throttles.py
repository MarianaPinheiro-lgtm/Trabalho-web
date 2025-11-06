from rest_framework.throttling import UserRateThrottle

class ConsultaEventosThrottle(UserRateThrottle):
    scope = 'consulta_eventos'

class InscricaoEventosThrottle(UserRateThrottle):
    scope = 'inscricao_eventos'