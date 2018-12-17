import pprint
import re

import requests
import xmltodict
from dateutil.parser import parse

from firefox.models import NewsFeed


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


def get_feed(url):
    retn = dict()

    response = requests.get(url)

    if response.status_code == 200:
        feed_dict = xmltodict.parse(response.text)

        pprint.pprint(feed_dict)

        if feed_dict:
            rss_dict = feed_dict.get('rss')

            if rss_dict:
                channel = rss_dict.get('channel')

                if channel:
                    retn['title'] = channel.get('title')
                    retn['link'] = channel.get('link')
                    retn['description'] = channel.get('description')

                    items = []
                    for item in channel.get('item'):
                        append_item = convert_keys(dict(item))
                        append_item['date'] = parse(append_item.get('pub_date'))
                        items.append(append_item)

                    retn['items'] = items

        else:
            print(feed_dict)

    return retn


def get_feeds():
    items = []

    feeds = NewsFeed.objects.filter(active=True)

    for feed in feeds:
        feed_items = get_feed(feed.url)

        items += feed_items

    return items
