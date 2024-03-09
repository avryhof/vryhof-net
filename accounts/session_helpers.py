from accounts.lib_utils import aware_now, load_model


def get_oauth_session(request, **kwargs):
    session_model = load_model("accounts.AuthSession")

    active = kwargs.get("active", True)

    session = None

    if active:
        sessions = session_model.objects.filter(expires_at__gte=aware_now())
    else:
        sessions = session_model.objects.all()

    if request.user.is_authenticated:
        try:
            session = sessions.get(user=request.user)
        except session_model.DoesNotExist:
            pass

    return session
