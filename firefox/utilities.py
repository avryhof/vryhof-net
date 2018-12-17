import datetime
import json
import pprint
import re

import requests
import xmltodict
from dateutil.parser import parse

from firefox.models import NewsFeed, NewsItem


def snake_to_camel(value, **kwargs):
    """
    Converts a snake_case key name to a camelCase key name, or vice versa.
    :param value: A string that you want to convert to another string type.
    :param kwargs:
        reverse - Convert from camelCase to snake_case
    :return: a converted string
    """
    do_reverse = kwargs.get('reverse', False)

    parts_ex = '([A-Z])' if do_reverse else '(_[A-Za-z])'
    parts = re.findall(parts_ex, value)

    for part in parts:
        if do_reverse:
            value = value.replace(part, '_%s' % part.lower())
        else:
            value = value.replace(part, part.upper().replace('_', ''))

    return value


def convert_keys(input_dict):
    """
    Convert all of the keys in a dict recursively from CamelCase to snake_case.
    Also strips leading and trailing whitespace from string values.
    :param input_dict:
    :return:
    """
    retn = {}

    for k, v in input_dict.items():
        new_key = snake_to_camel(str(k), reverse=True)
        new_key = new_key.replace('_i_d', '_id')
        if isinstance(v, dict):
            retn[new_key] = convert_keys(v)

        elif isinstance(v, list):
            retn[new_key] = convert_keys_list(v)

        else:
            if isinstance(v, str):
                retn[new_key] = v.strip()
            else:
                retn[new_key] = v

    return retn


def convert_keys_list(input_list):
    """
    Convert all of the keys in a list of dicts recursively from CamelCase to snake_case.
    Also strips leading and trailing whitespace from string values.
    :param input_list:
    :return:
    """
    retn_list = []

    for list_item in input_list:
        if isinstance(list_item, dict):
            retn_list.append(convert_keys(list_item))
        elif isinstance(list_item, list):
            retn_list.append(convert_keys_list(list_item))
        else:
            if isinstance(list_item, str):
                retn_list.append(list_item.strip())

            else:
                retn_list.append(list_item)

    return retn_list


def to_dict(input_ordered_dict):
    return json.loads(json.dumps(input_ordered_dict))


def get_feed(feed):
    url = feed.url
    retn = dict()

    response = requests.get(url)

    channel = None
    feed_items = None

    if response.status_code == 200:
        feed_dict = xmltodict.parse(response.text)

        if feed_dict:
            rss_dict = feed_dict.get('rss')
            rdf_dict = feed_dict.get('rdf:RDF')

            if rdf_dict:
                channel = rdf_dict.get('channel')
                feed_items = rdf_dict.get('item')

            elif rss_dict:
                channel = rss_dict.get('channel')
                feed_items = rss_dict.get('item', rss_dict.get('items'))

            if channel:
                retn['title'] = channel.get('title')
                retn['link'] = channel.get('link')
                retn['description'] = channel.get('description')

            if feed_items:
                items = []
                for item in feed_items:
                    append_item = convert_keys(dict(item))

                    item_date = datetime.datetime.now()
                    if 'pub_date' in append_item:
                        item_date = parse(append_item.get('pub_date'))

                    elif 'dc:date' in append_item:
                        item_date = parse(append_item.get('dc:date'))

                    append_dict = dict(
                        feed_id=feed.pk,
                        title=append_item.get('title'),
                        abstract=append_item.get('description'),
                        link=append_item.get('link'),
                        date=item_date
                    )

                    try:
                        news_item = NewsItem.objects.get(**append_dict)

                    except NewsItem.DoesNotExist:
                        NewsItem.objects.create(**append_dict)

                    items.append(append_dict)

                retn['items'] = items

    return retn


def get_feeds():
    items = []

    feeds = NewsFeed.objects.filter(active=True)

    for feed in feeds:
        feed_items = get_feed(feed)

        items += feed_items

    return items
