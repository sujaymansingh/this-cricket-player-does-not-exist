from slugify import slugify


class Country():
    def __init__(self, country_id, name):
        self.country_id = country_id
        self.name = name
        self.slug = slugify(self.name)


def get_all_countries():
    return [
        Country(country_id=1, name="England"),
        Country(country_id=2, name="Australia"),
        Country(country_id=3, name="South Africa"),
        Country(country_id=4, name="West Indies"),
        Country(country_id=5, name="New Zealand"),
        Country(country_id=6, name="India"),
        Country(country_id=7, name="Pakistan"),
        Country(country_id=8, name="Sri Lanka"),
        Country(country_id=9, name="Zimbabwe"),
        Country(country_id=25, name="Bangladesh"),
    ]


def get_country_by_slug(slug):
    return next(country for country in get_all_countries() if country.slug == slug)


def get_country_by_id(country_id):
    return next(country for country in get_all_countries() if country.country_id == country_id)
