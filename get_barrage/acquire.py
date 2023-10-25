import base64
import json
import re
import traceback

import execjs
import requests
from websocket import WebSocketApp

import new_pb2 as pb

# WebcastLikeMessage   点赞时间

ctx = execjs.compile(open('get_handle.js', 'r').read())
ctx2 = execjs.compile(open('sign.js', 'r', encoding='gb2312', errors='ignore').read())

pushproto_PushFrame = pb.pushproto_PushFrame()
pushproto_PushFrame.payloadtype = "hb"
ping_byte = pushproto_PushFrame.SerializeToString()


def fetch_live_room_info(url):
    s = requests.session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    }

    response = s.get(url, headers=headers)
    cookies_dict = dict(response.cookies)
    response = s.get(url, headers=headers, cookies=cookies_dict)
    ttwid = dict(response.cookies).get('ttwid')
    print(ttwid)
    # data_string = re.findall(r'<script id="RENDER_DATA" type="application/json">(.*?)</script>', response.text)[0]
    # data_dict = json.loads(unquote_plus(data_string))
    html = response.text
    pattern = r'self\.__pace_f\.push\(\[1,"a:\["\$","\$L11",null,(.*)]n"]\)</script>'
    json_data = re.findall(pattern, html.replace("\\", "").replace('"{', '{').replace('}"', '}'))
    # print(json_data)
    json_datas = json.loads(json_data[0])
    room_id = json_datas["state"]["roomStore"]['roomInfo']['roomId']
    # room_title = data_dict['app']['initialState']['roomStore']['roomInfo']["room"]['title']
    # room_user_count = data_dict['app']['initialState']['roomStore']['roomInfo']["room"]['user_count_str']
    X_Bogus = ctx2.call('my_function')
    wss_url = f"wss://webcast3-ws-web-lq.douyin.com/webcast/im/push/v2/?app_name=douyin_web&version_code=180800&webcast_sdk_version=1.3.0&update_version_code=1.3.0&compress=gzip&internal_ext=internal_src:dim|wss_push_room_id:{room_id}|wss_push_did:7140459943756301854|dim_log_id:202212281349305A73D850664DB518C21B|fetch_time:1681798944883|seq:1|wss_info:0-1681798944883-0-0|wrds_kvs:WebcastRoomStatsMessage-1672206566915058992_InputPanelComponentSyncData-1672187049066887013_WebcastRoomRankMessage-1672206560973484605&cursor=t-1681798944883_r-1_d-1_u-1_h-1&host=https://live.douyin.com&aid=6383&live_id=1&im_path=/webcast/im/fetch/&device_platform=web&room_id={room_id}&heartbeatDuration=1&signature={X_Bogus['X-Bogus']}&signature=00000000"
    # print(room_id, room_title, room_user_count)
    # return room_id, room_title, room_user_count, wss_url, ttwid
    return room_id, wss_url, ttwid


def keymessage(ws, byte, logid, payloadtype):
    webcast_im_Response = pb.webcast_im_Response()
    webcast_im_Response.ParseFromString(byte)
    # print("测试:",webcast_im_Response)
    for item in webcast_im_Response.messages:
        # print("测试2:", item.method)
        webcast_im_MemberMessage = pb.webcast_im_MemberMessage()
        webcast_im_MemberMessage.ParseFromString(item.payload)
        # 公共部分
        if item.method == 'WebcastMemberMessage':
            roomid = webcast_im_MemberMessage.common.roomid  # roomId
            douyinnum = webcast_im_MemberMessage.user.displayid  # 抖音号
            uid = webcast_im_MemberMessage.user.secuid  # uid
            avatarurl = webcast_im_MemberMessage.user.avatarthumb.urllist  # 头像url
            msgid = webcast_im_MemberMessage.common.msgid  # msgid
            nickname = webcast_im_MemberMessage.user.nickname  # 昵称
            print(f"roomId:{roomid},抖音号:{douyinnum},uid:{uid},头像url:{avatarurl},msgid:{msgid},昵称:{nickname}")

        if item.method == 'WebcastMemberMessage':  # 事件：用户进入直播间
            webcast_im_MemberMessage = pb.webcast_im_MemberMessage()
            webcast_im_MemberMessage.ParseFromString(item.payload)
            try:
                nickname = webcast_im_MemberMessage.user.nickname  # 昵称
                text = webcast_im_MemberMessage.common.displaytext.defaultpattern.strip('{0:user} ').strip('{1:string}')
                print(nickname + ':' + text)
            except:
                pass
        if item.method == 'WebcastChatMessage':  # 评论消息
            webcast_im_ChatMessage = pb.webcast_im_ChatMessage()
            webcast_im_ChatMessage.ParseFromString(item.payload)
            try:
                nickname = webcast_im_ChatMessage.user.nickname
                content = webcast_im_ChatMessage.content  # 评论内容
                comments_time = webcast_im_ChatMessage.eventtime  # 评论时间
                print(nickname, ':', content, comments_time)
            except:
                pass
        if item.method == 'WebcastGiftMessage':  # 礼物消息
            webcast_im_GiftMessage = pb.webcast_im_GiftMessage()
            webcast_im_GiftMessage.ParseFromString(item.payload)
            # 礼物名称、礼物id、礼物数量、礼物价值
            try:
                user = webcast_im_GiftMessage.user.nickname
                giftname = webcast_im_GiftMessage.gift.name  # 礼物名称
                giftid = webcast_im_GiftMessage.giftid  # 礼物id
                groupcount = webcast_im_GiftMessage.giftid  # 礼物数量

                print(user, giftname, giftid, groupcount)
            except:
                pass
        if item.method == 'WebcastSocialMessage':  # 网播社交讯息    关注类
            print(item.method)
            webcast_im_SocialMessage = pb.webcast_im_SocialMessage()
            webcast_im_SocialMessage.ParseFromString(item.payload)
            try:
                user = webcast_im_SocialMessage.user.nickname
                text = webcast_im_SocialMessage.common.displaytext.defaultpattern.strip('{0:user} ')
                # print(webcast_im_SocialMessage)
                print(user, text)
            except:
                pass
        if item.method == 'WebcastLikeMessage':  # 点赞了
            webcast_im_LikeMessage = pb.webcast_im_LikeMessage()
            webcast_im_LikeMessage.ParseFromString(item.payload)
            try:
                count = webcast_im_LikeMessage.count
                user = webcast_im_LikeMessage.user.nickname
                text = webcast_im_LikeMessage.common.displaytext.pieces[-1].stringvalue
                print(user, text, count, "次")
            except:
                pass

        if item.method == 'WebcastRanklistHourEntranceMessage':  # #直播间统计信息  榜单
            webcast_im_RoomStatsMessage = pb.webcast_im_RoomStatsMessage()
            webcast_im_RoomStatsMessage.ParseFromString(item.payload)
            try:
                print(webcast_im_RoomStatsMessage.displayshort)
            except:
                pass

        if item.method == 'WebcastFansclubMessage':  # 加入粉丝团   升级粉丝团
            webcast_im_SocialMessage = pb.webcast_im_SocialMessage()
            webcast_im_SocialMessage.ParseFromString(item.payload)
            try:
                user = webcast_im_SocialMessage.common.displaytext.pieces
                users = re.findall("nickname: \"(.*)\"", str(user))
                text = webcast_im_SocialMessage.common.displaytext.defaultpattern
                level = re.findall("stringvalue: \"(.*)\"", str(user))
                print(text.replace(" {0:user} ", users[0]).replace("{1:string}", level[0]))
            except:
                print(traceback.print_exc())
                pass
        if item.method == 'WebcastRoomStatsMessage':
            webcast_im_RoomStatsMessage = pb.webcast_im_RoomStatsMessage()
            webcast_im_RoomStatsMessage.ParseFromString(item.payload)
            try:
                liveroom_number = webcast_im_RoomStatsMessage.displayvalue
                print("在线人数：", liveroom_number)
            except:
                pass
        if item.method == 'WebcastRoomUserSeqMessage':
            print("发言累计", webcast_im_MemberMessage.actiondescription)

    needack = webcast_im_Response.needack
    if needack:
        internalext = webcast_im_Response.internalext
        # print(webcast_im_Response.cursor)
        ackpayload = ctx.call('get_ackpayload', internalext)
        # print(ackpayload)
        ackpayload = base64.b64decode(ackpayload)
        # print(ackpayload)
        pushproto_PushFrame2 = pb.pushproto_PushFrame()
        pushproto_PushFrame2.payloadtype = 'ack'
        pushproto_PushFrame2.payload = ackpayload
        pushproto_PushFrame2.logid = logid
        # print(pushproto_PushFrame2.SerializeToString())
        ws.send(pushproto_PushFrame2.SerializeToString())
    if payloadtype == 'close':
        ws.close()


def on_open(ws):
    print('连接成功！！！')
    ws.send(ping_byte)


def on_message(ws, content):
    # print('已获得数据：')
    pushproto_PushFrame.ParseFromString(content)
    logid = pushproto_PushFrame.logid
    payloadtype = pushproto_PushFrame.payloadtype
    # print(pushproto_PushFrame.headers)
    headers_list = {}
    for item in pushproto_PushFrame.headers:
        headers_list[item.key] = item.value
    # print(headers_list)
    if 'compress_type' in headers_list and headers_list['compress_type'] == 'gzip':
        payload = pushproto_PushFrame.payload
        payload = base64.b64encode(payload).decode()
        string = ctx.call('handle', payload)
        byte = base64.b64decode(string)
        keymessage(ws, byte, logid, payloadtype)
    else:
        payload = pushproto_PushFrame.payload
        keymessage(ws, payload, logid, payloadtype)


def on_ping(ws):
    ws.send(ping_byte)


def on_error(ws, errormessag):
    print("on_error:")
    print(errormessag)


def on_close(ws, content):
    print("连接已关闭！！！")


def run():
    web_url = "https://live.douyin.com/623302353683"
    # room_id, room_title, room_user_count, wss_url, ttwid = fetch_live_room_info(web_url)
    room_id, wss_url, ttwid = fetch_live_room_info(web_url)
    # print(f'欢迎来到{room_title}直播间，直播间人数{room_user_count}')
    ws = WebSocketApp(
        url=wss_url,
        header={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"

        },
        cookie=f"ttwid={ttwid}",
        on_open=on_open,
        on_message=on_message,
        # on_error=on_error,
        on_close=on_close,
        on_ping=on_ping
    )
    ws.run_forever(ping_interval=10)


if __name__ == '__main__':
    run()
