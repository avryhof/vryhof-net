import hashlib
import re


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def md5(s, raw_output=False):
    """Calculates the md5 hash of a given string"""
    res = hashlib.md5(s.encode())
    if raw_output:
        return res.digest()
    return res.hexdigest()


def convert_keys(input_value):
    return_value = input_value

    if isinstance(input_value, list):
        return_value = []

        for list_item in input_value:
            if isinstance(list_item, (dict, list)):
                return_value.append(convert_keys(list_item))
            else:
                if isinstance(list_item, str):
                    return_value.append(list_item.strip())

                else:
                    return_value.append(list_item)

    elif isinstance(input_value, dict):
        return_value = {}

        for k, v in list(input_value.items()):
            new_key_s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", k)
            new_key = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", new_key_s).lower()

            if isinstance(v, (dict, list)):
                return_value[new_key] = convert_keys(v)

            else:
                if isinstance(v, str):
                    return_value[new_key] = v.strip()
                else:
                    return_value[new_key] = v

    return return_value
