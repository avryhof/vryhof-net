import os


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
