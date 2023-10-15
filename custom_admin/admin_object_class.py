from django.urls import reverse


class AdminObject:
    obj = None

    app_name = ""
    model_name = ""

    admin_path = None
    app_url = None
    model_url = None
    object_url = None

    def __init__(self, obj):
        self.obj = obj

        self.app_name = obj.__class__._meta.app_label
        self.model_name = str(obj.__class__.__name__).lower()

        self.admin_index = reverse("admin:index")
        self.app_url = "".join([self.admin_index, self.app_name])
        self.model_url = "/".join([self.app_url, self.model_name])
        self.object_url = "/".join([self.model_url, str(obj.pk)])
        self.change_url = "/".join([self.object_url, "change/"])
        self.delete_url = "/".join([self.object_url, "delete/"])

    @property
    def change_link(self):
        return f'<a href="{self.change_url}">{str(self.obj)}</a>'

    @property
    def delete_link(self):
        return f'<a href="{self.delete_url}">{str(self.obj)}</a>'
