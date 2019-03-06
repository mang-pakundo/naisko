import sys
import json
import urllib
import urllib2

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

from enum import Enum

user_agent = 'okhttp/3.11.0'

modes = Enum('get_categories', 'category')
base_url = 'https://bff-prod.iwant.ph/api/OneCms/cmsapi/OTT'
this_plugin = int(sys.argv[1])
this_addon = xbmcaddon.Addon()

def build_url(path, base_url = base_url, params = {}):
    return '{base_url}{path}?{params}'.format(
            base_url = base_url, 
            path = path, 
            params = urllib.urlencode(params) if params else ''
        )
    
def http_request(url, params = {}, headers = []):
    opener = urllib2.build_opener()
    is_proxy_enabled = True if this_addon.getSetting('isProxyEnabled') == 'true' else False
    if is_proxy_enabled:
        opener = urllib2.build_opener(urllib2.ProxyHandler({'http': this_addon.getSetting('proxyAddress')}))
    headers.append(('X-Forwarded-For', this_addon.getSetting('xForwardedForIp')))
    headers.append(('User-Agent', user_agent))
    opener.addheaders = headers
    if params:
        data_encoded = urllib.urlencode(params)
        response = opener.open(url, data_encoded)
    else:
        response = opener.open(url)
    return response.read()
    
def get_json_response(url, params = {}):
    response = http_request(url, params = params)
    return json.loads(response)

def add_dir(name, id, mode, is_folder = True, **kwargs):
    query_string = {'id': id, 'mode': mode, 'name': name.encode('utf8')}
    url = '{addon_name}?{query_string}'.format(addon_name = sys.argv[0], query_string = urllib.urlencode(query_string))
    liz = xbmcgui.ListItem(name)
    info_labels = {"Title": name}
    for k, v in kwargs.iteritems():
        if not v:
            continue
        if k == 'info_labels':
            info_labels = dict(info_labels.items() + v.items())
        if k == 'list_properties':
            for list_property_key, list_property_value in v.iteritems():
                liz.setProperty(list_property_key, list_property_value)
        if k == 'art':
            liz.setArt(v)
            url = '{url}&{art_params}'.format(url = url, art_params = urllib.urlencode(v))
    liz.setInfo(type = "Video", infoLabels = info_labels)
    return xbmcplugin.addDirectoryItem(handle = this_plugin, url = url, listitem = liz, isFolder = is_folder)

def get_categories():
    url = build_url('/getInit')
    categories = get_json_response(url)
    for category in categories:
        add_dir(category['pageName'], category['pageCode'], MODES.category)
    xbmcplugin.endOfDirectory(this_plugin)

mode = modes.init
if mode == modes.get_categories:
    get_categories()