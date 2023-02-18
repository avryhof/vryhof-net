import hashlib
import importlib
import pprint


def lazy_load_class(module_name):
    loaded_module = importlib.import_module(module_name)

    return loaded_module


def get_val(input_obj, key, default=None):
    retn = default

    if isinstance(input_obj, dict):
        retn = input_obj.get(key, default)

    elif key in dir(input_obj):
        retn = getattr(input_obj, key, default)

    return retn


def md5(s, raw_output=False):
    """Calculates the md5 hash of a given string"""
    res = hashlib.md5(s.encode())
    if raw_output:
        return res.digest()
    return res.hexdigest()


def print_vals(input_object, hide_protected=True):
    retn = dict()

    for key in dir(input_object):
        if not hide_protected or (hide_protected and not key.startswith("_")):
            retn.update({key: get_val(input_object, key)})

    pprint.pprint(retn)
