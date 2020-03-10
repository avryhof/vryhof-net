from django.core.validators import RegexValidator

alphanumeric = RegexValidator(
    r"^[A-Za-z0-9\(\)\$\/\-@_&#:,\.\?!\s\n\r\t]*$", "Only letters, numbers, spaces and $@/-_&#/:,.?!_() are allowed.",
)

API_FORWARD_IP_KEY = "forward_ip"
API_GENERIC_FAILURE = "bad"
API_GENERIC_SUCCESS = "ok"
API_RESULT_KEY = "result"

NO_CACHE_HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
    "Expires": 0,
    "Pragma": "no-cache",
}

MOBILE_APP_AGENT = "ErWsatQyfJ93y4TnzUbaPtRwVa62tXbuTGNspRx8MweHsPaRr7"
