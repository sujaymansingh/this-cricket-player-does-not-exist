# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PlayerProfile(scrapy.Item):
    country_id = scrapy.Field()
    surname = scrapy.Field()
    known_as = scrapy.Field()
    fullname = scrapy.Field()
    profile = scrapy.Field()
