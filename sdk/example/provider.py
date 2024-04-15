import os
import logging

from urllib.parse import urlparse
from lxml import etree

from kubespider_plugin import utils as helper
from kubespider_plugin.sdk import SDK, ParserProvider
from kubespider_plugin.values import FileType, LinkType


def pre_download_file(event: dict, links: list) -> list:
    ret = []
    controller = helper.get_request_controller(
        cookie=event.get('cookies', None))
    for link in links:
        file = helper.download_torrent_file(link, controller)
        if file is not None:
            ret.append(file)

    return ret


def filter_links(event: dict, links: list) -> list:
    ret = []
    controller = helper.get_request_controller(
        cookie=event.get('cookies', None))
    for link in links:
        # For this situation(the href is "text.torrent"), we need to construct the link
        link_current = link
        if not link.startswith('magnet:') and not link.startswith('http'):
            url_data = urlparse(event.get('source'))
            link_current = os.path.join(
                url_data.scheme + "://" + url_data.netloc, link_current)

        link_type = helper.get_link_type(link_current, controller)
        if link_type != event.get('link_type', LinkType.torrent):
            logging.info('MagicSourceProvider skip %s, the link type does not match',
                         helper.format_long_string(link_current))
            continue
        ret.append(link_current)

    return ret


@SDK()
class Provider(ParserProvider):

    @staticmethod
    # pylint: disable=too-many-locals
    def get_links(source: str, **kwargs):
        event: dict = kwargs
        # extract the params from the event
        link_selector = event.get('link_selector', None)
        title_selector = event.get('title_selector', None)
        link_type = event.get('link_type', LinkType.magnet)
        file_type = event.get('file_type', FileType.video_mixed)
        charset = event.get('charset', 'utf-8')

        ret = []
        try:
            controller = helper.get_request_controller(
                cookie=event.get('cookies', None))
            resp = controller.get(source, timeout=30).content
        except Exception as err:
            logging.warning('MagicSourceProvider get links error:%s', err)
            return ret

        # decode html content, default utf-8, config in source_provider.yaml
        dom = etree.HTML(resp.decode(charset, 'ignore'))

        links = []
        # $URL is a builtin value, used to represent the original url
        if '$URL' == link_selector:
            links = [source]
        else:
            # Some website's link is not always at the same place.
            # So if not, you can define multiple selectors
            if isinstance(link_selector, list):
                for selector in link_selector:
                    links.extend([i.strip() for i in dom.xpath(selector)])
            else:
                links = [i.strip() for i in dom.xpath(link_selector)]

        links = filter_links(event, links)

        if link_type == LinkType.torrent:
            links = pre_download_file(event, links)

        if len(links) < 1:
            logging.info(
                "MagicSourceProvider get no links for %s", source)
            return ret

        if title_selector:
            titles = dom.xpath(title_selector)
            if len(titles) < 1:
                path = ''
            else:
                path = titles[0].strip()
        else:
            path = ''

        for link in links:
            logging.info('MagicSourceProvider find %s',
                         helper.format_long_string(link))
            ret.append({
                "url": link,
                "path": path,
                "file_type": file_type,
                "link_type": link_type,
            })
        return ret

    @staticmethod
    def should_handle(source: str, **kwargs):
        handle_host = kwargs.get('handle_host', None)
        if not handle_host:
            return False
        if urlparse(source).hostname in handle_host:
            return True
        return False
