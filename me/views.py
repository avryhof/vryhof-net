from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView

from me.forms import EditMeForm
from me.models import Member


class MeView(TemplateView):
    extra_css = ["css/member-profile.css"]
    extra_javascript = []

    template_name = "me.html"
    name = "Member Area"

    request = None

    def get_context_data(self, **kwargs):
        context = super(MeView, self).get_context_data(**kwargs)
        context["page_title"] = self.name
        context["extra_css"] = self.extra_css
        context["extra_javascript"] = self.extra_javascript
        context["request"] = self.request

        return context

    def get(self, request, *args, **kwargs):
        self.request = request
        context = self.get_context_data()

        try:
            profile = Member.objects.get(user=request.user)

        except Member.DoesNotExist:
            profile = Member.objects.create(user=request.user)
            return redirect("member-edit")

        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MeView, self).dispatch(*args, **kwargs)


class EditMeView(TemplateView):
    extra_css = ["css/member-profile.css"]
    extra_javascript = []

    template_name = "edit-me.html"
    name = "Update Profile"

    request = None

    def get_context_data(self, **kwargs):
        context = super(EditMeView, self).get_context_data(**kwargs)
        context["page_title"] = self.name
        context["extra_css"] = self.extra_css
        context["extra_javascript"] = self.extra_javascript
        context["request"] = self.request

        return context

    def get(self, request, *args, **kwargs):
        self.request = request
        context = self.get_context_data()

        try:
            profile = Member.objects.get(user=request.user)

        except Member.DoesNotExist:
            profile = Member.objects.create(user=request.user)

        context["form"] = EditMeForm(instance=profile)

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.request = request
        context = self.get_context_data()

        try:
            profile = Member.objects.get(user=request.user)

        except Member.DoesNotExist:
            return redirect("member-verify")

        else:
            form = EditMeForm(request.POST, request.FILES, instance=profile)

            if form.is_valid():
                form.save()

                return redirect("member-home")

        context["form"] = form

        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EditMeView, self).dispatch(*args, **kwargs)
