#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import json
import urllib
import urllib2

__version__ = '0.5.0'
__author__ = 'Liang Cha (ckmx945@gmail.com)'


'''
Python client SDK for Micro Message Public Platform API.
'''


try:
    import memcache
except Exception, e:
    print '\033[95mWrining: %s. use local FileCache.\033[0m' %e


(_HTTP_GET, _HTTP_POST, _HTTP_FILE) = range(3)

_CONTENT_TYPE_MEDIA = ('image/jpeg', 'audio/amr', 'video/mpeg4')

_MEIDA_TYPE = ('mpeg4', 'jpeg', 'jpg', 'gif', 'png', 'bmp', 'mp3', 'wav', 'wma', 'amr')

_CONTENT_TYPE_JSON= (
    'application/json; encoding=utf-8',
    'application/json',
    'text/plain',
    )

_API_URLS = (
    'https://api.weixin.qq.com/',
    'https://api.weixin.qq.com/cgi-bin/',
    )

_OTHER_FEATURES = (
    'semantic',         #微信智能接口
    'shackearound',     #微信摇一摇周边
    'sns',              #网页授权相关
    'datacube',         #数据统计
    'merchant',         #微信小店
    )


class APIError(StandardError):
    '''
    raise APIError if reciving json message indicating failure.
    '''

    def __init__(self, error_code, error_msg):
        self.error_code = error_code
        self.error_msg = error_msg
        StandardError.__init__(self, error_msg)

    def __str__(self):
        return '%d:%s' %(self.error_code, self.error_msg)


class AccessTokenError(APIError):
    '''
    raise AccessTokenError if reciving json message indicating failure.
    '''

    def __init__(self, error_code, error_msg):
        APIError.__init__(self, error_code, error_msg)

    def __str__(self):
        return APIError.__str__(self)


class JsonDict(dict):
    '''
    general json object that allows attributes to bound to and also behaves like a dict
    '''

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(r"'JsonDict' object has no attribute '%s'" %(attr))

        def __setattr__(self, attr, value):
            self[attr] = value


def _parse_json(s):
    ''' parse str into JsonDict '''

    def _obj_hook(pairs):
        o = JsonDict()
        for k, v in pairs.iteritems():
            o[str(k)] = v
        return o
    return json.loads(s, object_hook = _obj_hook)


def _encode_params(**kw):
    '''
    do url-encode parmeters

    >>> _encode_params(a=1, b='R&D')
    'a=1&b=R%26D'
    '''
    args = []
    body = None
    path = None
    for k, v in kw.iteritems():
        if k == 'body':
            body = v
            continue
        if k in _MEIDA_TYPE:
            continue
        if isinstance(v, basestring):
            qv = v.encode('utf-8') if isinstance(v, unicode) else v
            args.append('%s=%s' %(k, urllib.quote(qv)))
        else:
            if v is None:
                args.append('%s=' %(k))
            else:
                qv = str(v)
                args.append('%s=%s' %(k, urllib.quote(qv)))
    return ('&'.join(args), body)


def _encode_multipart(**kw):
    '''
    build a multipart/form-data body with randomly generated boundary
    '''
    data = []
    boundary = '----------%s' % hex(int(time.time()) * 1000)
    media_key = [key for key in _MEIDA_TYPE if key in kw.keys()]
    media_key = media_key[0] if media_key else 'null'
    fd = kw.get(media_key)
    media_type = kw.get('type') if kw.has_key('type') else 'null'
    content = fd.read() if hasattr(fd, 'read') else 'null'
    filename = getattr(fd, 'name', None)
    if filename is None: filename = '/tmp/fake.%s' %(media_key)
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"; filename="%s"' %(media_key, filename))
    data.append('Content-Length: %d' % len(content))
    data.append('Content-Type: %s/%s' %(media_type, media_key))
    data.append('Content-Transfer-Encoding: binary\r\n')
    data.append(content)
    data.append('--%s--\r\n' % boundary)
    if hasattr(fd, 'close'): fd.close()
    return '\r\n'.join(data), boundary


class WeiXinResponse(object):
    ''' To deal with response of the base class '''

    def __init__(self, resp):
        self._resp = resp

    def read(self):
        return self._resp.read()

    def close(self):
        self._resp.close()

    def __str__(self):
        return self._resp.headers['Content-Type']


class WeiXinJson(WeiXinResponse):
    ''' Json string '''

    def __init__(self, resp):
        WeiXinResponse.__init__(self, resp)

    def read(self):
        '''Check api or token error and return json'''
        rjson = _parse_json(self._resp.read())
        self._resp.close()
        if hasattr(rjson, 'errcode') and rjson.errcode != 0:
            if rjson.errcode in (40001, 40014, 41001, 42001):
                raise AccessTokenError(rjson.errcode, rjson.errmsg)
            raise APIError(rjson.errcode, rjson.errmsg)
        return rjson

    #response object close in read()
    def close(self):
        pass


class WeiXinMedia(WeiXinResponse):
    ''' Audio, Image, Video etc... '''

    def __init__(self, resp):
        WeiXinResponse.__init__(self, resp)


def _http_call(the_url, method, token,  **kw):
    '''
    send an http request and return a json object  if no error occurred.
    '''
    body = None
    params = None
    boundary = None
    (params, body) = _encode_params(**kw)
    if method == _HTTP_FILE:
        the_url = the_url.replace('https://api.', 'http://file.api.')
        body, boundary = _encode_multipart(**kw)
    if token == None:
        http_url = '%s?%s' %(the_url, params)
    else:
        the_url = '%s?access_token=%s' %(the_url, token)
        http_url = '%s&%s' %(the_url, params) if (method == _HTTP_GET or method == _HTTP_FILE) else the_url
    http_body = str(body) if (method == _HTTP_POST) else body
    req = urllib2.Request(http_url, data = http_body)
    if boundary: req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)
    try:
        resp = urllib2.urlopen(req, timeout = 8)
    except urllib2.HTTPError, e:
        if resp.headers['Content-Type'] == _CONTENT_TYPE_JSON:
            json = WeiXinJson(resp)
            return json.read()
    except Exception, e:
        raise e
    try:
        content_type = resp.headers['Content-Type']
    except KeyError, e:
        content_type = '??'
        resp.headers['Content_Type'] = content_type
    #print content_type
    if content_type in _CONTENT_TYPE_MEDIA:
        return WeiXinMedia(resp)
    elif content_type in _CONTENT_TYPE_JSON:
        json = WeiXinJson(resp)
        return json.read()
    else:
        return WeiXinResponse(resp)


class FileCache(object):
    '''
    the information is temporarily saved to the file.
    '''

    def __init__(self, path):
        self.path = path
        try:
            fd = open(self.path, 'rb'); data = fd.read(); fd.close()
            self.dict_data = json.loads(data)
        except Exception, e:
            self.dict_data = dict()

    def get(self, key):
        return self.dict_data.get(key)

    def set(self, key, value, time = 0):
        self.dict_data[key] = value

    def delete(self, key, time = 0):
        if self.dict_data.has_key(key): del self.dict_data[key]

    def save(self):
        data = (repr(self.dict_data)).replace('\'', '\"') #json must to use double quotation marks
        fd = open(self.path, 'wb'); fd.write(data); fd.close()

    def remove(self):
        import os
        try:
            os.remove(self.path)
        except Exception, e:
            pass

    def __str__(self):
        return repr(self.dict_data)


class WeiXinClient(object):
    '''
    API clinet using synchronized invocation.

    >>> fc = True
    'use memcache save access_token, otherwise use FileCache, path=[file_path | ip_addr]'
    '''
    def __init__(self, appID, appsecret, fc = True, path = '/tmp'):
        self.api_url= ''
        self.app_id = appID
        self.app_secret = appsecret
        self.access_token = None
        self.expires = 0
        self.fc = fc
        self.mc = FileCache('%s/access_token' %(path)) \
                if fc else memcache.Client([path], debug=0)

    def request_access_token(self):
        token_key = 'access_token_%s' %(self.app_id)
        expires_key = 'expires_%s' %(self.app_id)
        access_token = self.mc.get(token_key)
        expires = self.mc.get(expires_key)
        if not access_token or not expires or expires < int(time.time()):
            rjson =_http_call(_API_URLS[1] + 'token', _HTTP_GET,
                    None, grant_type = 'client_credential',
                    appid = self.app_id, secret = self.app_secret)
            self.access_token = str(rjson.access_token)
            self.expires = int(time.time()) + rjson.expires_in
            self.mc.set(token_key, self.access_token, time = rjson.expires_in)
            self.mc.set(expires_key, self.expires, time = rjson.expires_in)
            if self.fc: self.mc.save()
        else:
            self.access_token = str(access_token)
            self.expires = expires

    def del_access_token(self):
        token_key = 'access_token_%s' %(self.app_id)
        expires_key = 'expires_%s' %(self.app_id)
        self.access_token = None
        self.expires = 0
        self.mc.delete(token_key)
        self.mc.delete(expires_key)

    def refurbish_access_token(self):
        self.del_access_token()
        self.request_access_token()

    def set_access_token(self, token, expires_in, persistence=False):
        self.access_token = token
        self.expires = expires_in + int(time.time())
        if persistence:
            token_key = 'access_token_%s' %(self.app_id)
            expires_key = 'expires_%s' %(self.app_id)
            self.mc.set(token_key, token, time = expires_in)
            self.mc.set(expires_key, self.expires, time = expires_in)
            if self.fc: self.mc.save()

    def is_expires(self):
        return not self.access_token or int(time.time()) >= (self.expires - 10)

    def __getattr__(self, attr):
        self.api_url = _API_URLS[0] if attr in _OTHER_FEATURES else _API_URLS[1]
        return _Callable(self, attr)

    def __str__(self):
        return 'url=%s\napp_id=%s\napp_secret=%s\naccess_token=%s\nexpires=%d' \
            %(self.api_url, self.app_id, self.app_secret, self.access_token, self.expires)


class _Executable(object):

    def __init__(self, client, method, path):
        self._client = client
        self._method = method
        self._path = path

    def __call__(self, **kw):
        return _http_call('%s%s' %(self._client.api_url, self._path), \
            self._method, self._client.access_token, **kw)

    def __str__(self):
        return '_Executable (%s)' %(self._path)

    __repr__ = __str__



class _Callable(object):

    def __init__(self, client, name):
        self._client = client
        self._name = name

    def __getattr__(self, attr):
        if attr in ('dget', '_get'):
            return _Executable(self._client, _HTTP_GET, self._name)
        if attr == 'post':
            return _Executable(self._client, _HTTP_POST, self._name)
        if attr == 'file':
            return _Executable(self._client, _HTTP_FILE, self._name)
        name = '%s/%s' %(self._name, attr)
        return _Callable(self._client, name)

    def __str__(self):
        return '_Callable (%s)' %(self._name)

def test():
    ''' test the API '''
    pass

if __name__ == '__main__':
    test()
