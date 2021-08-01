import os

from square.client import Client

# Create an instance of the API Client
# and initialize it with the credentials
# for the Square account whose assets you want to manage

square_client = Client(
    access_token=os.environ.get("SQUARE_APP_TOKEN"),
    environment='sandbox',
)
