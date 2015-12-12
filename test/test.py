#!/usr/bin/env python
# -*- coding: utf-8 -*-

from weixin import WeiXinClient

if __name__ == '__main__':
    wc = WeiXinClient('your_appid', 'your_secret', fc = True, path='/tmp')
    #"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APPID&secret=APPSECRET"
    wc.request_access_token()

    data = '{"touser":"obMnLt3bf7t65jyEsa7vOtXphdu4", "msgtype":"text", "text":{ "content":"hello!"}}'
    #data = '{"touser":"obMnLt9Qx5ZfPdElO3DQblM7ksl0", "msgtype":"image", ' \
    #    '"image":{ "media_id":"OaPSe4DP-HF4s_ABWHEVDgMKOPCUoViID8x-yPUvwCfqTEA0whZOza4hGODiHs93"}}'
    key = '{"button":[{"type":"click","name":"test","key":"V1001_TEST"}]}'
    #"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=ACCESS_TOKEN"
    print wc.message.custom.send.post(body=data)
    #"https://api.weixin.qq.com/cgi-bin/user/info?access_token=ACCESS_TOKEN&openid=OPENID&lang=zh_CN"
    print wc.user.info._get(openid='obMnLt43lgfeeC8Ljn4-cLixEW6Q', lang='zh_CN')
    #"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=ACCESS_TOKEN"
    print wc.message.custom.send.post(body=data)
    #"https://api.weixin.qq.com/cgi-bin/user/get?access_token=ACCESS_TOKEN&next_openid=NEXT_OPENID"
    print wc.user.get._get(next_openid=None)
    #"http://file.api.weixin.qq.com/cgi-bin/media/upload?access_token=ACCESS_TOKEN&type=TYPE"
    print wc.media.upload.file(type='image', pic = open('./test.jpg', 'rb'))
    #"https://api.weixin.qq.com/cgi-bin/groups/create?access_token=ACCESS_TOKEN"
    print wc.groups.create.post(body='{"group":{"name":"test_group_01"}}')
    #"https://api.weixin.qq.com/cgi-bin/groups/update?access_token=ACCESS_TOKEN"
    print wc.groups.update.post(body='{"group":{"id":100,"name":"test"}}')
    #"https://api.weixin.qq.com/cgi-bin/groups/members/update?access_token=ACCESS_TOKEN"
    print wc.groups.members.update.post(body='{"openid":"obMnLt9Qx5ZfPdElO3DQblM7ksl0","to_groupid":100}')
    #"https://api.weixin.qq.com/cgi-bin/groups/getid?access_token=ACCESS_TOKEN"
    print wc.groups.getid.post(body='{"openid":"obMnLt9Qx5ZfPdElO3DQblM7ksl0"}')
    #"https://api.weixin.qq.com/cgi-bin/groups/get?access_token=ACCESS_TOKEN"
    print wc.groups.get._get()
    #"https://api.weixin.qq.com/cgi-bin/menu/create?access_token=ACCESS_TOKEN"
    print wc.menu.create.post(body=key)
    #"https://api.weixin.qq.com/cgi-bin/menu/get?access_token=ACCESS_TOKEN"
    print wc.menu.get._get()
    #"http://file.api.weixin.qq.com/cgi-bin/media/get?access_token=ACCESS_TOKEN&media_id=MEDIA_ID"
    print wc.media.get.file(media_id='OaPSe4DP-HF4s_ABWHEVDgMKOPCUoViID8x-yPUvwCfqTEA0whZOza4hGODiHs93')
