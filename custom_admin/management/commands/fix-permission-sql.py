from django.apps import apps
from django.conf import settings
from django.core.management import BaseCommand
from django.db import connection


class Command(BaseCommand):
    def handle(self, *args, **options):
        db_owner = settings.DATABASES["default"]["USER"]
        db_name = settings.DATABASES["default"]["NAME"]
        print(f"alter database {db_name} owner to {db_owner};")

        with connection.cursor() as cursor:
            for model in apps.get_models():
                table_name = model._meta.db_table

                print(f"grant all privileges on {table_name} to {db_owner};")
