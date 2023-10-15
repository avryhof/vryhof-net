from django.apps import apps
from django.core.management import BaseCommand
from django.db import connection


class Command(BaseCommand):
    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            for model in apps.get_models():
                table_name = model._meta.db_table
                pk_name = str(model._meta.pk).split(".")[-1]
                if "_ptr" in pk_name:
                    pk_name = f"{pk_name}_id"

                sql = f"SELECT setval(pg_get_serial_sequence('{table_name}', '{pk_name}'), max({pk_name})) FROM {table_name};"

                try:
                    cursor.execute(sql)
                except Exception as e:
                    print(f"{e}: {sql}")
