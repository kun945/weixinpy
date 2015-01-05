## Usage

Reference to 'test/test.py'.

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from weixin import WeiXinClient
from weixin import APIError
from weixin import AccessTokenError


if __name__ == '__main__':
    # 如果你有使用python-memcache 可以使用fc=False，path='ip:port'来启用memcache。
    # 如果你想问memcache能不能吃，还是老老实实用fc=True吧，path用来设置你保存临时文件的路径。
    #wc = WeiXinClient('您的AppID', '您的AppSecret', fc=True, path='/tmp')
    wc = WeiXinClient('wx1238b3917c06a851', '7f941e44d8e83add32401efe79e51cd3', fc=False, path='192.168.1.12:11211')
    # 使用其他api前必须先获取token
    wc.request_access_token()

    ################################################################################################
    # 获取用户列表 GET
    # https://api.weixin.qq.com/cgi-bin/user/get?access_token=ACCESS_TOKEN&next_openid=NEXT_OPENID
    #                                wc.user.get._get                     (next_openid=NEXT_OPENID)
    ###############################################################################################
    # 我们这里是第一次调用所以next_openid=None
    rjson = wc.user.get._get(next_openid=None)
    count = rjson.count
    id_list = rjson.data.openid
    while count < rjson.total:
        rjson = wc.user.get._get(next_openid=rjson.next_openid)
        count += rjson.count
        id_list.extend(rjson.openid)
    # 最后看看都有哪些用户
    print id_list

    ###############################################################################################
    # 发送文字信息 POST
    # https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=ACCESS_TOKEN
    #                                wc.message.custom.send.post(body=json_content)
    # 发送图片、语音、视频都是使用这个接口，只是body的内容不一样，具体参考官方说明
    ###############################################################################################
    for uid in id_list:
        content = '{"touser":"%s", "msgtype":"text", "text":{ "content":"hello!"}}' %uid
        #print 可以看有没有发送成功, 可以捕获api错误异常
        try:
            print wc.message.custom.send.post(body=content)
        except APIError, e:
            print e, uid
    
    
    ################################################################################################
    # 上传多媒体文件 POST（FILE为了和发送信息区别开来）
    # http://file.api.weixin.qq.com/cgi-bin/media/upload?access_token=ACCESS_TOKEN&type=TYPE
    #                                    wc.media.upload.file                     (type=TYPE, pic=fd)
    # type=<'image'|'voice'|'thumb'>，pic参数必须是有read()方法的对象。
    ###############################################################################################
    rjson = wc.media.upload.file(type='image', pic=open('/home/pi/ocr_pi.png', 'rb'))
    print rjson
    # 把上传的图片发出去
    for uid in id_list:
        content = '{"touser":"%s", "msgtype":"image", ' \
            '"image":{ "media_id":"%s"}}' % (uid, rjson.media_id)
        try:
            print wc.message.custom.send.post(body=content)
        except APIError, e:
            print e, uid

    ################################################################################################
    # 下载多媒体文件 GET
    # http://file.api.weixin.qq.com/cgi-bin/media/get?access_token=ACCESS_TOKEN&media_id=MEDIA_ID
    #                                    wc.media.get.file                     (media_id=MEDIA_ID, path=SAVE_PATH)
    # path参数是保存下载文件的路径                                  
    ###############################################################################################
    # 这里演示了如何捕获token失效的异常，产生这个异常就要更新token了
    try:
        print wc.media.get.file(media_id=rjson.media_id, path='./test2.png')
    except AccessTokenError, e:
        print e
        #更新token
        wc.refurbish_access_token()

    # 另外我们可以主动判断token是否失效, 这里只是在时间上验证，大多数的情况下是能正常工作的
    if wc.is_expires():
        wc.refurbish_access_token()

    print wc.menu.get._get()

    exit(0)
