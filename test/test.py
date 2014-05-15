#!/usr/bin/env python
# -*- coding: utf-8 -*-

from weixin import WeiXinClient

if __name__ == '__main__':
    wc = WeiXinClient('your_appid', 'your_secret', fc = True)
    wc.request_access_token()

    data = '{"touser":"obMnLt3bf7t65jyEsa7vOtXphdu4", "msgtype":"text", "text":{ "content":"今天不洗澡"}}'
    #data = '{"touser":"obMnLt9Qx5ZfPdElO3DQblM7ksl0", "msgtype":"image", ' \
    #    '"image":{ "media_id":"OaPSe4DP-HF4s_ABWHEVDgMKOPCUoViID8x-yPUvwCfqTEA0whZOza4hGODiHs93"}}'
    key = '{"button":[{"type":"click","name":"test","key":"V1001_TEST"}]}'
    print wc.message.custom.send.post(body=data)
    print wc.user.info._get(openid='obMnLt43lgfeeC8Ljn4-cLixEW6Q', lang='zh_CN')
    print wc.message.custom.send.post(body=data)
    print wc.user.get._get(next_openid=None)
    print wc.media.upload.file(type='image', pic = open('./test.jpg', 'rb'))
    print wc.groups.create.post(body='{"group":{"name":"test_group_01"}}')
    print wc.groups.update.post(body='{"group":{"id":100,"name":"test"}}')
    print wc.groups.members.update.post(body='{"openid":"obMnLt9Qx5ZfPdElO3DQblM7ksl0","to_groupid":100}')
    print wc.groups.getid.post(body='{"openid":"obMnLt9Qx5ZfPdElO3DQblM7ksl0"}')
    print wc.groups.get._get()
    print wc.menu.create.post(body=key)
    print wc.menu.get._get()
    print wc.media.get.file(media_id='OaPSe4DP-HF4s_ABWHEVDgMKOPCUoViID8x-yPUvwCfqTEA0whZOza4hGODiHs93')
