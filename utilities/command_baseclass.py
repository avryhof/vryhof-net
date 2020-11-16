import datetime
import logging
import math
import pprint

from django.conf import settings
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class ManagementCommand(BaseCommand):
    help = "Base Management Command."
    verbosity = 0
    init_time = None

    today = datetime.datetime.now().isoformat()[0:10]

    def _log_message(self, message, **kwargs):
        log_message = "%s: %s\n" % (datetime.datetime.now().isoformat()[0:19], message)

        if settings.DEBUG:
            logger.info(message)

        if kwargs.get("pretty", False):
            log_message = "%s:\n%s\n" % (datetime.datetime.now().isoformat()[0:19], pprint.pformat(message))

        if self.verbosity > 0:
            self.stdout.write(log_message)

    def _timer(self):
        if not self.init_time:
            self.init_time = datetime.datetime.now()
            self._log_message("Command initiated.")
        else:
            self._log_message("Command completed.")

            complete_time = datetime.datetime.now()
            command_total_seconds = (complete_time - self.init_time).total_seconds()
            command_minutes = math.floor(command_total_seconds / 60)
            command_seconds = command_total_seconds - (command_minutes * 60)

            self._log_message("Command took %i minutes and %i seconds to run." % (command_minutes, command_seconds))

    def handle(self, *args, **options):
        self._timer()

        self._timer()
