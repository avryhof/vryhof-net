from utilities.model_helper import load_model

from utilities.utility_functions import is_empty


def get_page_context(url_name, context):
    if not is_empty(url_name):
        page_model = load_model("frontend.Page")
        try:
            page = page_model.objects.get(url_name=url_name)
        except page_model.DoesNotExist:
            context["page"] = None
        else:
            context["page"] = page
            context["page_title"] = page.page_title

    return context
