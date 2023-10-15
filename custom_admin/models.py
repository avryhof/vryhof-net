import inspect
import logging
import os

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.safestring import mark_safe

from custom_admin import name as appname
from custom_admin.admin_object_class import AdminObject

logger = logging.getLogger(__name__)


class ExceptionLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    user = models.ForeignKey(get_user_model(), blank=True, null=True, on_delete=models.CASCADE)
    exception = models.TextField(blank=True, null=True)
    traceback = models.TextField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    path = models.TextField(blank=True, null=True)
    filename = models.CharField(max_length=255, blank=True, null=True)
    function_name = models.CharField(max_length=255, blank=True, null=True)
    line_number = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "Exception at {} for user {}".format(self.path, self.user, self.function_name)

    @classmethod
    def add(cls, request, exception, **kwargs):
        debug_filename = os.path.basename(inspect.stack()[1][1])
        debug_function_name = inspect.stack()[1][3]
        debug_line_number = inspect.stack()[1][2]

        try:
            ExceptionLog.objects.create(
                user=request.user,
                exception=exception,
                traceback=exception.__traceback__,
                message=kwargs.get("message", None),
                path=request.build_absolute_uri(),
                filename=debug_filename,
                function_name=debug_function_name,
                line_number=debug_line_number,
            )
        except Exception as e:
            logger.error("Error creating Exception Log: {} - For exception: {}".format(e, exception))

    @property
    def formatted_traceback(self):
        return mark_safe("<pre>{}</pre>".format(self.traceback))

    @property
    def troubleshooter_link(self):
        ao = AdminObject(self)
        return ao.change_link
