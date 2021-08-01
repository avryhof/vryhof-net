import datetime

import iso18245
import uuid0 as uuid0
from dateutil.parser import parse
from django.db.models import (
    Model,
    ForeignKey,
    CharField,
    IntegerField,
    TextField,
    UUIDField,
    CASCADE,
    PositiveIntegerField,
    EmailField,
    TimeField,
    URLField,
    SET_NULL,
    DateTimeField,
    DecimalField,
)
from django.utils.text import slugify

from catalog.constants import (
    SQUARE_WEEKDAYS,
    DAY_MONDAY,
    SQUARE_STATUS,
    STATUS_ACTIVE,
    SQUARE_LOCATION_TYPE,
    SQUARE_CAPABILITIES,
)
from catalog.square_base import square_client
from catalog.utils import generate_abbreviation
from gis.models import AbstractStreetAddress
from utilities.debugging import log_message


class Location(AbstractStreetAddress):
    location_id = CharField(max_length=255, blank=True, null=True)
    location_status = CharField(max_length=10, choices=SQUARE_STATUS, default=STATUS_ACTIVE)
    location_type = CharField(max_length=10, choices=SQUARE_LOCATION_TYPE, default="PHYSICAL")
    business_name = CharField(max_length=255, blank=True, null=True)
    description = TextField(blank=True, null=True)
    phone_number = CharField(max_length=32, blank=True, null=True)
    email = EmailField(blank=True, null=True)
    website_url = URLField(blank=True, null=True)
    facebook_url = URLField(blank=True, null=True)
    instagram_username = CharField(max_length=255, blank=True, null=True)
    twitter_username = CharField(max_length=255, blank=True, null=True)
    country = CharField(max_length=2, blank=True, null=True)
    created_at = DateTimeField(null=True)
    currency = CharField(max_length=10, blank=True, null=True)
    language_code = CharField(max_length=10, blank=True, null=True)
    mcc = CharField(max_length=10, blank=True, null=True)
    merchant_id = CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return self.business_name if self.business_name is not None else self.name

    @property
    def mcc_description(self):
        return iso18245.get_mcc(self.mcc)

    @property
    def hours(self):
        return [x.as_dict() for x in LocationHours.objects.filter(location=self)]

    @property
    def capabilities(self):
        return [x.capability for x in LocationCapability.objects.filter(location=self)]

    def as_dict(self):
        if not self.postal_code:
            self.link_postal_code()

        return {
            "name": self.name,
            "business_name": self.business_name if self.business_name else self.name,
            "capabilities": self.capabilities,
            "coordinates": {"latitude": self.latitude, "longitude": self.longitude},
            "address": {
                "address_line_1": self.address1,
                "address_line_2": self.address2,
                "locality": self.city,
                "administrative_district_level_1": self.postal_code.admin_code1,
                "administrative_district_level_2": self.postal_code.admin_name2,
                "postal_code": self.zip_code,
                "country": self.postal_code.country_code,
            },
            "business_hours": {"periods": [self.hours]},
            "description": self.description,
            "business_email": self.email,
            "website_url": self.website_url,
            "facebook_url": self.facebook_url,
        }

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(Location, self).save(force_insert, force_update, using, update_fields)

        location_body = {"location": self.as_dict()}

        if self._state.adding:
            result = square_client.locations.create_location(body=location_body)
            if "location" in result:
                self.location_id = result.get("location").get("id")
                super(Location, self).save(force_insert, force_update, using, update_fields)
        else:
            result = square_client.locations.update_location(location_id=self.location_id, body=location_body)
        return result.is_success()

    def download(self):
        result = square_client.locations.retrieve_location(location_id=self.location_id)
        if result.is_success():
            location = result.get("location")

            self.name = (location.get("name"),)
            self.business_name = (location.get("business_name"),)
            self.country = (location.get("country"),)
            self.created_at = (parse(location.get("created_at")),)
            self.currency = (location.get("currency"),)
            self.language_code = (location.get("language_code"),)
            self.mcc = (location.get("mcc"),)
            self.merchant_id = (location.get("merchant_id"),)
            self.location_status = (location.get("status"),)
            self.location_type = (location.get("type"),)
            self.address1 = (location.get("address").get("address_line_1"),)
            self.address2 = (location.get("address").get("address_line_2"),)
            self.city = (location.get("address").get("locality"),)
            self.zip_code = (location.get("address").get("postal_code"),)

            capabilities = location.get("capabilities")
            for capability in capabilities:
                try:
                    LocationCapability.objects.get(location=self, capability=capability)
                except LocationCapability.DoesNotExist:
                    LocationCapability.objects.create(location=self, capability=capability)
            LocationCapability.objects.filter(location=self).exclude(capability__in=capabilities).delete()
        return result.is_success()


class LocationHours(Model):
    location = ForeignKey(Location, null=True, on_delete=CASCADE)
    day_of_week = CharField(max_length=10, choices=SQUARE_WEEKDAYS, default=DAY_MONDAY)
    start_local_time = TimeField(default=datetime.time(hour=9, minute=0))
    end_local_time = TimeField(default=datetime.time(hour=5, minute=0))

    def as_dict(self):
        return dict(
            day_of_week=self.day_of_week, start_local_time=self.start_local_time, end_local_time=self.end_local_time
        )


class LocationCapability(Model):
    location = ForeignKey(Location, null=True, on_delete=CASCADE)
    capability = CharField(max_length=50, choices=SQUARE_CAPABILITIES, default="CREDIT_CARD_PROCESSING")


class Catalog(Model):
    location = ForeignKey(Location, null=True, on_delete=SET_NULL)
    name = CharField(max_length=255, blank=True, null=True)
    version = IntegerField(blank=True, null=True)

    def __str__(self):
        retn = self.name

        if self.location is not None:
            retn = "{} at {}".format(self.name, self.location)

        return retn

    def list(self):
        if self.version is not None:
            result = square_client.catalog.list_catalog(types="ITEM", version=self.version)
        else:
            result = square_client.catalog.list_catalog(types="ITEM")
        cat = result.body.get("objects") if result.is_success() else result.errors

        for item in cat:
            object_id = item.get("id")
            item_data = item.get("item_data")
            self.version = item.get("version")
            try:
                catalog_item = CatalogItem.objects.get(object_id=object_id)
            except CatalogItem.DoesNotExist:
                catalog_item = CatalogItem.objects.create(
                    catalog=self,
                    name=item_data.get("name"),
                    description=item_data.get("description"),
                    item_abbreviation=item_data.get("abbreviation"),
                    object_id=object_id,
                )
            else:
                catalog_item.name = item_data.get("name")
                catalog_item.description = item_data.get("description")
                catalog_item.item_abbreviation = item_data.get("abbreviation")
                catalog_item.save()

            for variation in item_data.get("variations"):
                v_object_id = variation.get("id")
                v_item_data = variation.get("item_variation_data")
                try:
                    variant = CatalogVariant.objects.get(object_id=v_object_id)
                except CatalogVariant.DoesNotExist:
                    variant = CatalogVariant.objects.create(
                        catalog_item=catalog_item,
                        name=v_item_data.get("name"),
                        price=v_item_data.get("price_money").get("amount"),
                        object_id=v_object_id,
                    )
                else:
                    variant.catalog_item = catalog_item
                    variant.name = v_item_data.get("name")
                    variant.price = v_item_data.get("price_money").get("amount")
                    variant.object_id = v_object_id
                    variant.save()

                catalog_item.save()

        self.save()

        return cat


class CatalogItem(Model):
    catalog = ForeignKey(Catalog, blank=True, null=True, on_delete=CASCADE)
    name = CharField(max_length=255, blank=True, null=True)
    description = TextField(blank=True, null=True)
    item_abbreviation = CharField(max_length=255, blank=True, null=True)
    item_key = UUIDField(blank=True, null=True)
    item_id = CharField(max_length=255, blank=True, null=True)
    object_id = CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

    def update_id_mappings(self, id_mappings=[]):
        for id_mapping in id_mappings:
            object_id = id_mapping.get("client_object_id ")
            try:
                variant = CatalogVariant.objects.get(catalog_item=self, variant_key=object_id)
            except CatalogVariant.DoesNotExist:
                pass
            else:
                variant.object_id = object_id
                variant.save_id()

    def delete(self, using=None, keep_parents=False):
        super().delete(using, keep_parents)

        result = square_client.catalog.delete_catalog_object(object_id=self.object_id)
        response = result.body if result.is_success() else result.errors
        log_message(response, pretty=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.item_abbreviation or self.item_abbreviation is None:
            self.item_abbreviation = generate_abbreviation(self.name)

        if not self.item_key or self.item_key is None:
            self.item_key = str(uuid0.generate())

        if not self.item_id:
            self.item_id = "#{}".format(slugify(self.name))
            self.object_id = "#{}".format(slugify(self.name))

        super().save(force_insert, force_update, using, update_fields)

        itemid = self.item_id
        if not self._state.adding:
            if self.object_id is not None:
                itemid = self.object_id

        body = self.as_dict(itemid)

        log_message(body, pretty=True)

        if self.variants.count() > 0:
            result = square_client.catalog.upsert_catalog_object(body=body)
            catalog_item = result.body if result.is_success() else result.errors

            if "catalog_object" in catalog_item:
                self.catalog.version = catalog_item.get("catalog_object").get("version")
                self.object_id = catalog_item.get("catalog_object").get("id")
                super().save(force_insert, force_update, using, update_fields)

            try:
                id_mappings = catalog_item.get("id_mappings", [])
            except AttributeError:
                log_message(catalog_item, pretty=True)
            else:
                self.update_id_mappings(id_mappings)

    @property
    def idempotency_key(self):
        return str(uuid0.generate())

    @property
    def variants(self):
        return CatalogVariant.objects.filter(catalog_item=self)

    @property
    def abbreviation(self):
        pieces = self.name.split()
        return self.name[0:2] if len(pieces) == 1 else "".join([x[0] for x in pieces])

    def get_item(self):
        version = self.catalog.version
        if not version:
            result = square_client.catalog.retrieve_catalog_object(object_id=self.item_key)
        else:
            result = square_client.catalog.retrieve_catalog_object(object_id=self.item_key, catalog_version=version)

        item = result.body if result.is_success() else result.errors
        if "object" in item:
            item = item.get("object")

        return item

    def as_dict(self, item_id):
        variations = [variant.as_dict() for variant in self.variants]

        return {
            "idempotency_key": self.idempotency_key,
            "object": {
                "type": "ITEM",
                "id": item_id,
                "item_data": {
                    "name": self.name,
                    "description": self.description,
                    "abbreviation": self.item_abbreviation,
                    "variations": variations,
                },
            },
        }


class CatalogVariant(Model):
    catalog_item = ForeignKey(CatalogItem, blank=True, null=True, on_delete=CASCADE)
    name = CharField(max_length=255, blank=True, null=True)
    item_id = UUIDField(blank=True, null=True)
    price = PositiveIntegerField(null=True)
    variant_key = CharField(max_length=255, blank=True, null=True)
    object_id = CharField(max_length=255, blank=True, null=True)
    rfid_id = CharField(max_length=255, blank=True, null=True)
    upc_id = CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{} variant of {}".format(self.name, self.catalog_item)

    def save_id(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.item_id:
            self.item_id = str(uuid0.generate())

        if not self.variant_key:
            self.variant_key = "#{}".format(slugify(self.name))
            self.object_id = "#{}".format(slugify(self.name))

        super().save(force_insert, force_update, using, update_fields)

        if self.catalog_item is not None:
            self.catalog_item.save()

    def as_dict(self):
        return {
            "type": "ITEM_VARIATION",
            "id": self.object_id,
            "item_variation_data": {
                "item_id": self.catalog_item.object_id,
                "name": self.name,
                "pricing_type": "FIXED_PRICING",
                "price_money": {"amount": self.price, "currency": "USD"},
            },
        }


class Discount(Model):
    name = CharField(max_length=255, blank=True, null=True)
    discount_id = CharField(max_length=255, blank=True, null=True)


class Order(Model):
    location = ForeignKey(Location, null=True, on_delete=CASCADE)
    order_id = CharField(max_length=255, blank=True, null=True)
    order_key = UUIDField(blank=True, null=True)

    @property
    def idempotency_key(self):
        return str(uuid0.generate())

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)

        if self._state.adding:
            result = square_client.orders.create_order(body=self.as_dict())
        else:
            result = square_client.orders.update_order(order_id=self.order_id, body=self.update_dict())

        return result.is_success()

    def as_dict(self):
        return {
            "order": {
                "location_id": self.location.location_id,
                "reference_id": self.order_id,
                "line_items": [item.as_dict() for item in OrderItem.objects.filter(order=self)],
                "taxes": [tax.as_dict() for tax in OrderTax.objects.filter(order=self)],
                "discounts": [discount.as_dict() for discount in OrderDiscount.objects.filter(order=self)],
            },
            "idempotency_key": self.idempotency_key,
        }

    def update_dict(self):
        return {
            "order": {
                "location_id": self.location.location_id,
                "line_items": [item.as_dict() for item in OrderItem.objects.filter(order=self)],
                "taxes": [tax.as_dict() for tax in OrderTax.objects.filter(order=self)],
                "discounts": [discount.as_dict() for discount in OrderDiscount.objects.filter(order=self)],
                "version": 1,
            },
            "fields_to_clear": ["line_items", "taxes", "discounts"],
            "idempotency_key": self.idempotency_key,
        }


class OrderDiscount(Model):
    order = ForeignKey(Order, null=True, on_delete=CASCADE)
    uid = CharField(max_length=128, blank=True, null=True)
    name = CharField(max_length=255, blank=True, null=True)
    amount = DecimalField(max_digits=6, decimal_places=2, null=True)
    percentage = DecimalField(max_digits=3, decimal_places=2, null=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.uid:
            self.uid = slugify(self.name)

        super().save(force_insert, force_update, using, update_fields)

    def as_dict(self):
        retn = {"uid": self.uid, "name": self.name, "scope": "ORDER"}

        if self.amount is not None:
            retn.update(amount=str(self.amount))
        elif self.percentage is not None:
            retn.update(percentage=str(self.percentage))

        return retn


class OrderTax(Model):
    order = ForeignKey(Order, null=True, on_delete=CASCADE)
    tax_id = CharField(max_length=255, blank=True, null=True)
    name = CharField(max_length=255, blank=True, null=True)
    percentage = DecimalField(max_digits=3, decimal_places=2)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.tax_id:
            self.tax_id = slugify(self.name)

        super().save(force_insert, force_update, using, update_fields)

    def as_dict(self):
        return {"uid": self.tax_id, "name": self.name, "percentage": str(self.percentage), "scope": "ORDER"}


class OrderItem(Model):
    order = ForeignKey(Order, null=True, on_delete=CASCADE)
    name = CharField(max_length=255, blank=True, null=True)
    quantity = PositiveIntegerField(default=1)
    base_price = DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    catalog_item = ForeignKey(CatalogItem, null=True, on_delete=CASCADE)
    catalog_variant = ForeignKey(CatalogVariant, null=True, on_delete=CASCADE)

    def as_dict(self):
        if self.catalog_item:
            retn = {
                "quantity": str(self.quantity),
                "catalog_object_id": self.catalog_item.item_key,
            }
            if self.catalog_variant:
                retn.update({"modifiers": [{"catalog_object_id": self.catalog_variant.item_id}]})

            item_discounts = []
            for item_discountd in OrderItemDiscount.objects.filter(order=self.order, item=self):
                item_discounts.append({"discount_uid": item_discountd.uid})
            if len(item_discounts) > 0:
                retn.update({"applied_discounts": item_discounts})
        else:
            retn = {
                "name": self.name,
                "quantity": str(self.quantity),
                "base_price_money": {"amount": self.base_price, "currency": "USD"},
            }
            item_discounts = []
            for item_discountd in OrderItemDiscount.objects.filter(order=self.order, item=self):
                item_discounts.append({"discount_uid": item_discountd.uid})
            if len(item_discounts) > 0:
                retn.update({"applied_discounts": item_discounts})
        return retn


class OrderItemDiscount(Model):
    order = ForeignKey(Order, null=True, on_delete=CASCADE)
    item = ForeignKey(OrderItem, null=True, on_delete=CASCADE)
    name = CharField(max_length=255, blank=True, null=True)
    percentage = DecimalField(max_digits=3, decimal_places=2)
    uid = CharField(max_length=255, blank=True, null=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.uid:
            self.uid = slugify(self.name)

        super().save(force_insert, force_update, using, update_fields)
