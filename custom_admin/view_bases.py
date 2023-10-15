from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView


class CustomAdminPageView(TemplateView):
    extra_css = []
    extra_javascript = []
    template_name = "admin/custom-admin-page.html"
    name = "Custom Admin Page"

    requests = None

    def get_context_data(self, **kwargs):
        context = super(CustomAdminPageView, self).get_context_data(**kwargs)
        context["page_title"] = self.name
        context["extra_css"] = self.extra_css
        context["extra_javascript"] = self.extra_javascript
        context["request"] = self.request

        return context

    @method_decorator(csrf_protect)
    @method_decorator(login_required(login_url="admin:login"))
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(CustomAdminPageView, self).dispatch(*args, **kwargs)



