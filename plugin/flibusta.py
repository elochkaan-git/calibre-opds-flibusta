from contextlib import closing
from urllib.parse import urljoin

from qt.core import QUrl

from calibre import browser, guess_extension
from calibre.gui2 import open_url
from calibre.gui2.store import StorePlugin
from calibre.gui2.store.search_result import SearchResult
from calibre.gui2.store.web_store_dialog import WebStoreDialog
from calibre.utils.opensearch.query import Query
from calibre.utils.opensearch.description import Description
from calibre.utils.xml_parse import safe_xml_fromstring


class StoreFlibusta(StorePlugin):
    """Actual store plugin for Flibusta
    """

    # URL of OpenSearch file
    store_open_search = 'https://flibusta.is/opds-opensearch.xml'
    # URL of store
    store_url = 'https://flibusta.is/'

    def open(self, gui=None, parent=None, detail_item=None, external=False):
        if external or self.config.get('open_external', False):
            open_url(QUrl(self.store_url))
        else:
            d = WebStoreDialog(self.gui, self.store_url, parent, detail_item, self.create_browser)
            d.setWindowTitle(self.name)
            d.set_tags(self.config.get('tags', ''))
            d.exec()

    def search(self, query, max_results=10, timeout=60):
        # Searching best template and put placeholders
        open_search_description = Description(self.store_open_search)
        url_template = open_search_description.get_best_template()
        if not url_template:
            return
        open_search_query = Query(url_template)
        open_search_query.searchTerms = query
        open_search_query.count = max_results
        search_url = open_search_query.url() # get final url for searching

        counter = max_results
        br = browser()

        with closing(br.open(search_url, timeout=timeout)) as xml:
            document = safe_xml_fromstring(xml.read())
            # search all entries
            for entry in document.xpath('//*[local-name() = "entry"]'):
                if counter <= 0:
                    break
                counter -= 1

                s_res = SearchResult()
                s_res.title = ' '.join(entry.xpath('./*[local-name() = "title"]/text()')).strip()
                s_res.author = ', '.join(entry.xpath('./*[local-name() = "author"]//*[local-name() = "name"]//text()')).strip()
                s_res.price = '$0.00'
                s_res.detail_item = ''.join(entry.xpath('./*[local-name() = "id"]/text()')).strip()
                s_res.drm = SearchResult.DRM_UNLOCKED

                for link in entry.xpath('./*[local-name() = "link"]'):
                    href, rel, type = link.get('href'), link.get('rel'), link.get('type')

                    if href and rel and type:
                        if 'http://opds-spec.org/image' in rel or 'http://opds-spec.org/thumbnail' in rel:
                            s_res.cover_url = urljoin(self.store_url, href)
                        elif 'alternate' in rel:
                            s_res.detail_item = urljoin(self.store_url, href)
                        elif 'http://opds-spec.org/acquisition' in rel:
                            ext = guess_extension(type)
                            if ext:
                                s_res.downloads[ext[1:].upper().strip()] = urljoin(self.store_url, href)
                            elif "application/fb2" in type:
                                s_res.downloads['FB2'] = urljoin(self.store_url, href)
                            elif "application/html" in type:
                                s_res.downloads['HTML'] = urljoin(self.store_url, href)
                            elif "application/txt" in type:
                                s_res.downloads['TXT'] = urljoin(self.store_url, href)
                            elif "application/rtf" in type:
                                s_res.downloads['RTF'] = urljoin(self.store_url, href)
                            elif "application/epub" in type:
                                s_res.downloads['EPUB'] = urljoin(self.store_url, href)
                            elif "application/x-mobipocket-ebook" in type:
                                s_res.downloads['MOBI'] = urljoin(self.store_url, href)
                            else:
                                continue
                
                s_res.formats = ', '.join(s_res.downloads.keys()).strip()
                yield s_res





            


