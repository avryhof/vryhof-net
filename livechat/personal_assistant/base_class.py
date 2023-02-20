from django.conf import settings

from utilities.debugging import log_message


class BaseClass(object):
    debug = False
    log_level = False

    def __init__(self, **kwargs):
        self.debug = kwargs.get("debug", getattr(settings, "DEBUG"))
        self.log_level = kwargs.get("log_level", getattr(settings, "LOG_LEVEL", False))

    def log(self, message):
        if self.debug:
            log_message(message)
