# weixinpy
----
这是一个简单的python版本的腾讯微信公共平台的sdk。<br>

## 更新日志
----

### 当前版本 version 0.5.0
----
1、HTTP GET方法关键字由'_get'改为'dget'(原来的'_get'仍然可用)。<br>
2、修改完善媒体文件的上传(支持"mpeg4/jpeg/jpg/png/gif/bmp/mp3/wma/wav/amr"), 具体看usage。<br>

### version 0.4.9
----
1、修复bug。<br>
2、默认采用FileCache方式保存access_token。<br>
3、增加对“微信智能接口”、“微信摇一摇周边”、“网页授权”、“数据统计”、“微信小店”的支持。<br>

## Usage
----
初始化过程：
```
from weixin import WeixinClient, APIError, AccessTokenError
# 如果你有使用python-memcache 可以使用fc=False，path='ip:port'来启用memcache
# 默认使用FileCache, 保存在/tmp/access_token, 可以通过path='path'来设置保存目录
wc = WeiXinClient('您的AppID', '您的AppSecret')
# 使用其他api前必须先获取token
wc.request_access_token()
```

请求用户列表：
API URL：https://api.weixin.qq.com/cgi-bin/user/get?access_token=ACCESS_TOKEN&next_openid=NEXT_OPENID
```
# 我们这里是第一次调用所以next_openid=None
rjson = wc.user.get.dget(next_openid=None)
count = rjson.count
id_list = rjson.data.openid
while count < rjson.total:
    rjson = wc.user.get.dget(next_openid=rjson.next_openid)
    count += rjson.count
    id_list.extend(rjson.openid)
# 最后看看都有哪些用户
print id_list
```

发送文字信息：
API URL：https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=ACCESS_TOKEN
```
for uid in id_list:
    content = '{"touser":"%s", "msgtype":"text", "text":{ "content":"hello!"}}' %uid
    #print 可以看有没有发送成功, 可以捕获api错误异常
    try:
        print wc.message.custom.send.post(body=content)
    except APIError, e:
        print e, uid
```

上传并发送媒体：
API URL：http://file.api.weixin.qq.com/cgi-bin/media/upload?access_token=ACCESS_TOKEN&type=TYPE
```
rjson = wc.media.upload.file(type='image', png=open('/home/pi/ocr_pi.png', 'rb'))
print rjson
# 把上传的图片发出去
for uid in id_list:
    content = '{"touser":"%s", "msgtype":"image", ' \
        '"image":{ "media_id":"%s"}}' % (uid, rjson.media_id)
        print wc.message.custom.send.post(body=content)
```

下载媒体文件，如何判断token失效：
API URL：http://file.api.weixin.qq.com/cgi-bin/media/get?access_token=ACCESS_TOKEN&media_id=MEDIA_ID
```
# 这里演示了如何捕获token失效的异常，产生这个异常就要更新token了
try:
    rm = wc.media.get.file(media_id=rjson.media_id)
    print rm
    open('./test.png', 'rb').write(rm.read())
    rm.close()
except AccessTokenError, e:
    print e
    #更新token
    wc.refurbish_access_token()

# 另外我们可以主动判断token是否失效, 这里只是在时间上验证，大多数的情况下是能正常工作的
if wc.is_expires():
    wc.refurbish_access_token()
```

微信智能接口
```
q = '{"query":"查一下鹰潭的天气", "city":"鹰潭", "category":"weather", "appid":"%s"}' %(your_pid)
print wc.semantic.semproxy.search.post(body=q)
```

媒体文件上传
```
print wc.media.upload.file(type='video', mpeg4=open('./a.mp4', 'rb'))
print wc.media.upload.file(type='image', jpeg=open('./a.jpg', 'rb'))
print wc.media.upload.file(type='image', gif=open('./a.gif', 'rb'))
print wc.media.upload.file(type='voice', amr=open('./a.amr', 'rb'))
print wc.media.upload.file(type='voice', wma=open('./a.wma', 'rb'))
```

Have Fun!

