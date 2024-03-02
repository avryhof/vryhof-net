from accounts.models import GraphSession
from accounts.utils import aware_now


def get_oauth_session(request, **kwargs):
    active = kwargs.get("active", True)

    session = None

    if active:
        sessions = GraphSession.objects.filter(expires_at__gte=aware_now())
    else:
        sessions = GraphSession.objects.all()

    if request.user.is_authenticated:
        try:
            session = sessions.get(user=request.user)
        except GraphSession.DoesNotExist:
            pass

    if session is None:
        try:
            session = sessions.get(django_session__session_key=request.session.session_key)
        except GraphSession.DoesNotExist:
            pass
        else:
            if request.user.is_authenticated:
                session.user = request.user
                session.save()

    return session
