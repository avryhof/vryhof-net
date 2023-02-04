from me.models import Member
from utilities.utility_functions import is_empty


def get_display_name(user):
    if user.is_authenticated:
        retn = user.username
        try:
            profile = Member.objects.get(user=user)
        except Member.DoesNotExist:
            name = [str(x) for x in [user.first_name, user.last_name] if not is_empty(x)]
            if not is_empty(name):
                retn = " ".join(name)
        else:
            name = [str(x) for x in [profile.first_name, profile.last_name] if not is_empty(x)]
            if not is_empty(name):
                retn = " ".join(name)
    else:
        retn = "Log In"

    return retn
