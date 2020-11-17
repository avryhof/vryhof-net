import random
import string

from django.contrib.auth import get_user_model
from django.db.models import Model, URLField, CharField, ForeignKey, CASCADE

from utilities.helpers import md5


class SubsonicServer(Model):
    """
    We don't actually want to store the password for the subsonic server,
    so we just store a hash/salt combination to use for API calls.
    """

    user = ForeignKey(get_user_model(), on_delete=CASCADE)
    url = URLField(blank=True, null=True)
    username = CharField(max_length=200, blank=True, null=True)
    password_hash = CharField(max_length=255, blank=True, null=True)
    password_salt = CharField(max_length=255, blank=True, null=True)

    def change_password(self, password):
        salt_length = random.randint(6, 12)
        self.password_salt = "".join(
            random.choice(string.ascii_letters + "1234567890_")
            for i in range(salt_length)
        )
        salted_password = password + self.password_salt
        self.password_hash = md5(salted_password)
