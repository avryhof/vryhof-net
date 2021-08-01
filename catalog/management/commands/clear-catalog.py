from django.core.management import BaseCommand

from catalog.square_base import square_client
from utilities.debugging import log_message


class Command(BaseCommand):
    def handle(self, *args, **options):
        result = square_client.catalog.list_catalog(types="ITEM,ITEM_VARIATION")

        if result.is_success():
            objects = result.body.get("objects")

            del_result = square_client.catalog.batch_delete_catalog_objects(
                body={"object_ids": [x.get("id") for x in objects]}
            )

            if del_result.is_success():
                log_message(del_result.body, pretty=True)
            elif del_result.is_error():
                print(del_result.errors)

        elif result.is_error():
            print(result.errors)
