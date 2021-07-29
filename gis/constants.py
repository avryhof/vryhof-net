COUNTRIES = ["AZ", "GU", "MP", "PR", "US", "VI"]

ACCURACY_CHOICES = ((1, "Estimated"), (4, "Geoname ID"), (6, "Centroid of addresses or shape"))

URBAN = 50000
SUBURBAN = 2500
RURAL = 10

CLASS_URBAN = "URBAN"
CLASS_SUBURBAN = "SUBURBAN"
CLASS_RURAL = "RURAL"
POPULATION_CLASSIFICATIONS = (
    (CLASS_URBAN, "Urban"),
    (CLASS_SUBURBAN, "Suburban"),
    (CLASS_RURAL, "Rural"),
)
