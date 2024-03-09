import os

from accounts.lib_utils import not_empty, log_message
from utilities.model_helper import load_model


def get_profile(request):
    if request.user.is_authenticated:
        member_profile = load_model("me.Member")
        try:
            profile = member_profile.objects.get(user=request.user)
        except member_profile.DoesNotExist:
            profile_model = load_model("accounts.UserPrefs")
            try:
                profile = profile_model.objects.get(user=request.user)
            except profile_model.DoesNotExist:
                return request.user
            else:
                log_message("Profile from accounts.UserPrefs")
        else:
            log_message("Profile from me.Member")

        if not_empty(profile):
            return profile

    return None


def profile_files(member):
    folder = os.path.join("members", str(member.user.username))
    # if not os.path.exists(folder):
    #     os.makedirs(folder)

    return folder


def photo_upload_path(instance, filename):
    folder = profile_files(instance)

    return os.path.join(folder, filename)


def handle_profile_file(profile, f):
    filename = str(f)
    file_path = os.path.join(profile_files(profile), filename)
    with open(file_path, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)
