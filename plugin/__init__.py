# -*- coding: utf-8 -*-

from calibre.customize import StoreBase
from calibre.utils.localization import _


class StoreFlibustaMeta(StoreBase):
    """Meta information about plugin
    """

    author = 'Alexander Elyshkin'
    description = _('Независимый библиотечный ресурс.')
    name = 'Флибуста'
    version = (1, 0, 1)

    actual_plugin = 'calibre_plugins.store_flibusta.flibusta:StoreFlibusta'
    drm_free_only = True
    headquarters = 'RU'
    formats = ['FB2', 'EPUB', 'MOBI']
