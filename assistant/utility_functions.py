import json


def request_to_dict(request):
    if isinstance(request.data, str):
        data = json.loads(request.data)

    elif isinstance(request.data, dict):
        data = request.data

    else:
        data = {}

    return data

