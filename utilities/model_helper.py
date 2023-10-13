from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured

from utilities.utility_functions import is_empty


def load_model(app_name, model_name=None):
    if is_empty(model_name):
        accessor = app_name
        model_name = accessor.split(".")[-1]
    else:
        accessor = ".".join([app_name, model_name])

    try:
        return django_apps.get_model(accessor, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(f"{accessor} must be of the form 'app_label.model_name'")

    except LookupError:
        raise ImproperlyConfigured(f"{accessor} refers to model '{model_name}' that has not been installed")
