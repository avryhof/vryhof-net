import datetime
import fnmatch
import glob
import os
import re

import dateutil
from django.conf import settings

from utilities.debugging import log_message


def find_files(base_dir, **kwargs):
    pattern = kwargs.get("pattern", False)
    re_pattern = kwargs.get("re_pattern", False)

    match_files = []
    all_files = glob.glob(os.path.join(base_dir, "**"), recursive=True)

    for file in all_files:
        if pattern and fnmatch.fnmatch(file, pattern):
            match_files.append(file)

        elif re_pattern and re.match(re_pattern, file):
            match_files.append(file)

    return match_files


def get_media_dir(*dirname):
    media_root = getattr(settings, "MEDIA_ROOT")
    media_dir = os.path.join(media_root, *dirname)

    if not os.path.exists(media_dir):
        os.makedirs(media_dir)

    return media_dir


def get_media_url(*dirname):
    media_root = getattr(settings, "MEDIA_URL")
    media_dir = "%s%s" % (media_root, *dirname)

    return media_dir


def remove_files(data_file_dir, pattern):
    files_to_remove = glob.glob(os.path.join(data_file_dir, pattern))
    for file_to_remove in files_to_remove:
        os.remove(file_to_remove)


def get_newest_file(path, **kwargs):
    filename_extension = kwargs.get("filename_extension", "xls*")
    filename_mask = kwargs.get("filename_mask", "*.%s*" % filename_extension)

    file_mask = os.path.join(path, filename_mask)
    files = glob.glob(file_mask)

    if len(files) == 1:
        source_file = files[0]

    else:
        files = glob.iglob(file_mask)
        source_file = max(files, key=os.path.getmtime)

    return source_file


def handle_uploaded_file(request_file, **kwargs):
    """
    Adapted from https://docs.djangoproject.com/en/2.2/topics/http/file-uploads/
    :param request_file: an UploadedFile - https://docs.djangoproject.com/en/2.2/ref/files/uploads/#django.core.files.uploadedfile.UploadedFile
    :return:
        False if there are any exceptions with saving the file.

        ELSE: The fully qualified path of where the uploaded file is saved.
    """
    accept_types = kwargs.get("accept_types", False)

    retn = False

    if not accept_types or request_file.content_type in accept_types:
        media_root_normalized = os.path.join(*os.path.split(settings.MEDIA_ROOT))
        target_dir = os.path.join(media_root_normalized, "uploaded")
        target_file = os.path.join(target_dir, request_file.name)

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        try:
            with open(target_file, "wb+") as destination:
                for chunk in request_file.chunks():
                    destination.write(chunk)
            destination.close()

        except Exception as e:
            retn = False
        else:
            retn = target_file

    return retn


def is_file_stale(filename):
    retn = False

    if filename:
        one_week_ago = datetime.datetime.now() - dateutil.relativedelta.relativedelta(weeks=1)

        if not os.path.exists(filename) or datetime.datetime.fromtimestamp(os.path.getmtime(filename)) < one_week_ago:
            retn = True

    return retn


def file_get_contents(file_name):
    file_content = False

    if os.path.isfile(file_name):
        with open(file_name, "r") as file_handle:
            file_content = file_handle.read()

            file_handle.close()

    return file_content


def file_put_contents(file_name, file_content):
    try:
        with open(file_name, "w") as fh:
            fh.write(file_content)
            fh.close()
    except Exception as e:
        log_message(e)
        retn = False
    else:
        retn = True

    return retn
