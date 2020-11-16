import json
import re


def convert_keys(input_dict):
    """
    Convert all of the keys in a dict recursively from CamelCase to snake_case.
    Also strips leading and trailing whitespace from string values.
    :param input_dict:
    :return:
    """
    retn = {}

    for k, v in list(input_dict.items()):
        new_key_s = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", k)
        new_key = re.sub("([a-z0-9])([A-Z])", r"\1_\2", new_key_s).lower()
        if isinstance(v, dict):
            retn[new_key] = convert_keys(v)

        elif isinstance(v, list):
            retn[new_key] = convert_keys_list(v)

        else:
            if isinstance(v, str):
                retn[new_key] = v.strip()
            else:
                retn[new_key] = v

    return retn


def convert_keys_list(input_list):
    """
    Convert all of the keys in a list of dicts recursively from CamelCase to snake_case.
    Also strips leading and trailing whitespace from string values.
    :param input_list:
    :return:
    """
    retn_list = []

    for list_item in input_list:
        if isinstance(list_item, dict):
            retn_list.append(convert_keys(list_item))
        elif isinstance(list_item, list):
            retn_list.append(convert_keys_list(list_item))
        else:
            if isinstance(list_item, str):
                retn_list.append(list_item.strip())

            else:
                retn_list.append(list_item)

    return retn_list


def slugify(text):
    return re.sub(r"[\W_]+", "-", text)


def to_dict(input_ordered_dict):
    return json.loads(json.dumps(input_ordered_dict))
