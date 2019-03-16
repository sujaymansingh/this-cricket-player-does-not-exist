# -*- coding: utf-8 -*-
import scrapy
import urllib
from urllib.parse import urlencode, urljoin

from .. import items


class ProfilesSpider(scrapy.Spider):
    name = "profiles"
    allowed_domains = ["espncricinfo.com"]

    def start_requests(self):
        """We start off with each player page (supplying the ids of each test
        playing nation).
        """
        for country_id in [1, 2, 3, 4, 5, 6, 7, 8, 9, 25]:
            url = get_player_listing_url(country_id)
            meta = {"country_id": country_id}
            yield scrapy.Request(url, self.parse_listing, meta=meta)

    def parse_listing(self, response):
        """Parse a listing page to get all the player links, supplying the
        country and surname as meta.
        """
        pattern = "//li[@class='ciPlayername']/a[@class='ColumnistSmry']"
        for link in response.xpath(pattern):
            initials_and_surname = link.select("text()").extract()[0]
            surname = get_surname(initials_and_surname)
            country_id = response.meta["country_id"]
            href = link.select("@href").extract()[0]

            new_meta = {"surname": surname, "country_id": country_id}
            url = urljoin("http://www.espncricinfo.com", href)
            yield scrapy.Request(url, self.parse_player_profile, meta=new_meta)

    def parse_player_profile(self, response):
        """Extract the player details from the profile page.
        """
        surname = response.meta["surname"]
        country_id = response.meta["country_id"]

        yield items.PlayerProfile(
            country_id=country_id,
            surname=surname,
            profile=self.profile(response),
            known_as=self.known_as(response),
            fullname=self.fullname(response))

    def profile(self, response):
        path = "//div[@id='shrtPrfl']/p/text()"
        raw_profile = response.xpath(path).extract()
        return [line.replace("\n", " ") for line in raw_profile if line and line.strip()]

    def known_as(self, response):
        path = "//div[@class='ciPlayernametxt']//h1/text()"
        return response.xpath(path).extract()[0]

    def fullname(self, response):
        for item in response.xpath("//p[@class='ciPlayerinformationtxt']"):
            # There are of the form <b>key</b> <span>value</span>.
            key = item.select("b/text()").extract()
            if key == ["Full name"]:
                return item.select("span/text()").extract()[0]


def get_surname(initials_and_surname):
    """Extract the surname from a name. It assumes that any token that is only
    upper case characters is a list of initials.

    >>> get_surname('HJ Simpson')
    'Simpson'
    >>> get_surname('de Beaumarche')
    'de Beaumarche'
    """
    # We want to get rid of some abbreviations.
    initials_and_surname = initials_and_surname.replace("Hon.", "")
    initials_and_surname = initials_and_surname.replace("Rev.", "")

    raw_tokens = initials_and_surname.split()

    # And we want to ignore any titles.
    titles = ["sir"]
    tokens = [token for token in raw_tokens if token.lower() not in titles]

    non_uppercase_tokens = [token for token in tokens if token != token.upper()]
    return " ".join(non_uppercase_tokens)


def get_player_listing_url(country_id):
    """This returns the url that lists all test players for the given
    country.
    """
    params = {"country": country_id, "class": 1}
    base_url = u"http://www.espncricinfo.com/ci/content/player/caps.html"
    return u"{0}?{1}".format(base_url, urlencode(params))
