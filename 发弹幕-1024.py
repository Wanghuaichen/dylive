import base64
import hashlib
import random
import time
import urllib.parse

import numpy as np
import requests
# from loguru import logger
from faker import Faker
fake = Faker('zh_CN')
from 纯算_signatuer import get_ac_signatuer


def str_to_Uint8Array(a):
    b = len(a) >> 1
    c = b << 1
    e = list(range(16))
    d = 0
    t = 0
    _0x19ae48 = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                 None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                 None, None, None, None, None, None, None, None, None, None, None, None, None, None, 0, 1, 2, 3, 4, 5,
                 6, 7, 8, 9, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                 None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                 None, None, None, None, None, None, None, 10, 11, 12, 13, 14, 15];
    while t < c:
        e[d] = _0x19ae48[ord(a[t])] << 4 | _0x19ae48[ord(a[t + 1])]
        d += 1
        t += 2
    return e


def get_w9(w):
    x = [w[0], w[10], w[1], w[11], w[2], w[12], w[3], w[13], w[4], w[14], w[5], w[15], w[6], w[16], w[7], w[17], w[8],
         w[18]]
    temp = 0
    for index, i in enumerate(x[:-1]):
        if temp == 0:
            temp = int(i) ^ int(x[index + 1])
        else:
            temp = temp ^ x[index + 1]
    x.append(temp)
    return x


def rc4(key, plaintext):
    S = list(range(256))
    j = 0
    out = []

    # KSA
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]

    # PRGA
    i = j = 0
    for char in plaintext:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(ord(char) ^ S[(S[i] + S[j]) % 256])

    return base64.b64encode(bytes(out)).decode('utf-8')


def get_w(data, key, ts, ubcode, ua, salt):
    plaintext_arr = str_to_Uint8Array(hashlib.md5(hashlib.md5(data.encode()).digest()).hexdigest())

    salt_arr = str_to_Uint8Array(hashlib.md5(np.array(str_to_Uint8Array(salt), dtype='uint8')).hexdigest())
    ua_arr = str_to_Uint8Array(hashlib.md5(rc4(key, ua).encode()).hexdigest())
    # canvas = random.randint(536919696, 556919696)
    canvas = 536919696

    w = list(range(19))
    w[0] = 64  # 固定
    w[1] = 1  # 固定
    w[2] = plaintext_arr[14]
    w[3] = salt_arr[14]
    w[4] = ua_arr[14]
    w[5] = 101
    w[6] = (int(ts) >> 8) & 255
    w[7] = canvas >> 24 & 255  # canvas 指纹 _0x5bc542， 536919696 >> 24 & 255
    w[8] = canvas >> 8 & 255  # canvas 指纹 _0x5bc542， 536919696>> 8 & 255

    w[10] = 0.00390625  # 固定
    w[11] = ubcode
    w[12] = plaintext_arr[15]
    w[13] = salt_arr[15]
    w[14] = ua_arr[15]
    w[15] = (int(ts) >> 16) & 255
    w[16] = (int(ts) >> 0) & 255
    w[17] = canvas >> 16 & 255  # canvas 指纹 _0x5bc542， 536919696 >> 16 & 255
    w[18] = canvas >> 0 & 255  # canvas 指纹 _0x5bc542， 536919696 >> 0 & 255

    print("w-->", w)
    w1 = get_w9(w)
    print("w1-->", w1)
    return w1
    # return [64,0.00390625,1,8,172,140,69,63,253,150,100,137,82,43,74,226,150,241,35]


def get_xbogus(data, ua):
    """
    1. 明文转数组w
    2. 数组w生成新的数组w1
    3. 使用w1进行编码，然后rc4加密
    5. 头部拼接两位字节
    6. 按照特定规则拼接xbogus
    :param data:
    :return:
    """
    ubcode = 0
    salt = 'd41d8cd98f00b204e9800998ecf8427e'
    salt2 = "Dkdpgh4ZKsQB80/Mfvw36XI1R25-WUAlEi7NLboqYTOPuzmFjJnryx9HVGcaStCe="
    key_ua = b'\x00\x01\x00'
    key_data = 'ÿ'.encode('latin-1')
    # ts = round(time.time(), 3)
    ts = 1698133355.053  # js位置 234 766 0

    w1 = get_w(data, key_ua, ts, ubcode, ua, salt)

    temp = rc4(key_data, ''.join([chr(int(_)) for _ in w1]))

    temp = '\u0002'.encode('latin-1') + key_data + base64.b64decode(temp)

    xbogus = ''
    for _ in range(7):
        n = ((temp[3 * _]) << 16) | ((temp[3 * _ + 1]) << 8) | temp[3 * _ + 2]

        xbogus += salt2[(n & 16515072) >> 18]
        xbogus += salt2[(n & 258048) >> 12]
        xbogus += salt2[(n & 4032) >> 6]
        xbogus += salt2[(n & 63) >> 0]

    return xbogus


def send_msg(msg, ua):
    headers = {
        'authority': 'live.douyin.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'referer': 'https://live.douyin.com/549964440159',
        'sec-ch-ua': '"Chromium";v="118", "Microsoft Edge";v="118", "Not=A?Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': ua,
    }
    cookies = {
        'FORCE_LOGIN': '%7B%22videoConsumedRemainSeconds%22%3A180%7D',
        'passport_csrf_token': '5bc918c55cb7b453d2f9f53a09bfae4a',
        'passport_csrf_token_default': '5bc918c55cb7b453d2f9f53a09bfae4a',
        'strategyABtestKey': '%221698113097.754%22',
        '__live_version__': '%221.1.1.4685%22',
        'xgplayer_user_id': '434058921454',
        'ttcid': 'a350ebcc275b40b98b31a80a1be837d031',
        'download_guide': '%223%2F20231024%2F0%22',
        'pwa2': '%220%7C0%7C3%7C0%22',
        'stream_recommend_feed_params': '%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1920%2C%5C%22screen_height%5C%22%3A1080%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A20%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22',
        'home_can_add_dy_2_desktop': '%221%22',
        'VIDEO_FILTER_MEMO_SELECT': '%7B%22expireTime%22%3A1698735029499%2C%22type%22%3A1%7D',
        'volume_info': '%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.5%7D',
        'device_web_cpu_core': '20',
        'device_web_memory_size': '8',
        'webcast_local_quality': 'ld',
        'csrf_session_id': '5c64367707bcb12360d5ab883ed9170d',
        '__ac_nonce': '06537693e006f6a7bf683',
        '__ac_signature': '_02B4Z6wo00f01d8-KZwAAIDAz2DMpX6vEwXfHi0AABL6DdRuXNceWXKOmMHgJKYX.2QtApI7mt4zuh.4a1k8mryu11vRjebfQmyhACBMalvPLoqZ1dSer9BacyyiOZwsHK2Ttrft8ArAzWNg7f',
        'webcast_leading_last_show_time': '1698130240217',
        'webcast_leading_total_show_times': '1',
        's_v_web_id': 'verify_lo3zbxyx_sKBApElJ_4Tv6_4Srz_BCAM_Oo9EDAXd8JWy',
        'n_mh': 'nges5CKsZ3KBE3nh1GWEeJZl8vVrxrrIbIDOUNzmaHI',
        'sso_uid_tt': 'ff0beb3328a017d81d97d6a9b2b383ce',
        'sso_uid_tt_ss': 'ff0beb3328a017d81d97d6a9b2b383ce',
        'toutiao_sso_user': '1e8044544bd3304048004017cab6c49d',
        'toutiao_sso_user_ss': '1e8044544bd3304048004017cab6c49d',
        'passport_auth_status': '985d7963ff0bfcaad3eddfdf58000666%2C',
        'passport_auth_status_ss': '985d7963ff0bfcaad3eddfdf58000666%2C',
        'uid_tt': '51bc5fd66527cb2974ef0f3f655ab1be',
        'uid_tt_ss': '51bc5fd66527cb2974ef0f3f655ab1be',
        'sid_tt': 'bee5744bae6adb914135455a530087dd',
        'sessionid': 'bee5744bae6adb914135455a530087dd',
        'sessionid_ss': 'bee5744bae6adb914135455a530087dd',
        'passport_assist_user': 'Cjyp_xBTWVAz7XcJ2hGdU8cz7Yl6mYhVpRbEam0Sk5zBrrbHUMHGjhIvx6GGIfc0XvLjsxgr824tbvozoTEaSgo8YkYaz82klntPZaUnCAVB4RF3Pnm7C84ARkp_0C2u640eBmYRrMywF9ntT7o8PDXSfeXgr6NPDsouSQhNEJu1vw0Yia_WVCABIgED_vgyBQ%3D%3D',
        'sid_ucp_sso_v1': '1.0.0-KDJlYjhlYzQ5MmY1OWEzM2VjZjg4YmU2NGZlMDYzZjcxZjY3YjliMDMKHQiNjOiF7gEQxNjdqQYY7zEgDDDV3cDLBTgGQPQHGgJscSIgMWU4MDQ0NTQ0YmQzMzA0MDQ4MDA0MDE3Y2FiNmM0OWQ',
        'ssid_ucp_sso_v1': '1.0.0-KDJlYjhlYzQ5MmY1OWEzM2VjZjg4YmU2NGZlMDYzZjcxZjY3YjliMDMKHQiNjOiF7gEQxNjdqQYY7zEgDDDV3cDLBTgGQPQHGgJscSIgMWU4MDQ0NTQ0YmQzMzA0MDQ4MDA0MDE3Y2FiNmM0OWQ',
        'publish_badge_show_info': '%220%2C0%2C0%2C1698131017141%22',
        '_bd_ticket_crypt_doamin': '3',
        '_bd_ticket_crypt_cookie': 'dbd2f6ef4b3ae51358195ca156951542',
        '__security_server_data_status': '1',
        'sid_guard': 'bee5744bae6adb914135455a530087dd%7C1698131020%7C5183993%7CSat%2C+23-Dec-2023+07%3A03%3A33+GMT',
        'sid_ucp_v1': '1.0.0-KGE2ZjI0YjljMzNmNjI1OTQ5YTkyYjc4NTg4ZWJkYTU0MjUzNTBkMjIKGQiNjOiF7gEQzNjdqQYY7zEgDDgGQPQHSAQaAmhsIiBiZWU1NzQ0YmFlNmFkYjkxNDEzNTQ1NWE1MzAwODdkZA',
        'ssid_ucp_v1': '1.0.0-KGE2ZjI0YjljMzNmNjI1OTQ5YTkyYjc4NTg4ZWJkYTU0MjUzNTBkMjIKGQiNjOiF7gEQzNjdqQYY7zEgDDgGQPQHSAQaAmhsIiBiZWU1NzQ0YmFlNmFkYjkxNDEzNTQ1NWE1MzAwODdkZA',
        'live_can_add_dy_2_desktop': '%221%22',
        'bd_ticket_guard_client_data': 'eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCTTIxNHZDNVZRUENLbmRrVFBFUVpvLzR0UEVpRDFCbHZGME5RSmZ4MUZaaktkWFlkRVBUZUtwTlJ3OE9pWm1FY2hEaC9qYytONFhxSnpDR2preUpTc1k9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D',
        'passport_fe_beating_status': 'true',
        'odin_tt': 'da290f7ac24bdf9d55ee45510eade088b01d11781dee2615bfa5caf6526c448b7443749d02961fe3e485b235abe37ccf',
        'tt_scid': 'ySvAjCqJtvnHQV4laHvpp7lC3ZAIw6f6wPG2cUmY8f.PIUohwjJwgyC2AnwUoY-N67a4',
        # 'msToken': 'H4j9lVk89iUwb8G6A6xpLHDVrCyd0G8byLlnHBGm8svZowS8P7u2AOI5-LoyWRxG_7NXhTMcALW_loltXfOstjU6Cs9XgvjvLTaPWmRX8uHV4Myvm3F_IFmVUZ_o',
        # 'msToken': 'cWvO0NKE9K-x5fbXGzBO8RZJaf86_LlY9Y9iK0FfygfaCNOOnaHITnTlXG4XyQsK1oRqCTVQ-wlk0GCTe6I5K3PeJPXfcDBtc5llOE6nOa_mWwm5MVc=',
        'IsDouyinActive': 'false',
    }
    url = "https://live.douyin.com/webcast/room/chat/"
    params = {
        "aid": "6383",
        "app_name": "douyin_web",
        "live_id": "1",
        "device_platform": "web",
        "language": "zh-CN",
        "cookie_enabled": "true",
        "screen_width": "1920",
        "screen_height": "1080",
        "browser_language": "zh-CN",
        "browser_platform": "Win32",
        "browser_name": "Edge",
        "browser_version": "118.0.2088.61",
        "room_id": "7293676729145608999",
        "content": msg,
        "type": "0",
        # 'msToken': 'H4j9lVk89iUwb8G6A6xpLHDVrCyd0G8byLlnHBGm8svZowS8P7u2AOI5-LoyWRxG_7NXhTMcALW_loltXfOstjU6Cs9XgvjvLTaPWmRX8uHV4Myvm3F_IFmVUZ_o',

    }

    params['X-Bogus'] = get_xbogus(urllib.parse.urlencode(params).replace('%2F', '/').replace('%3D', '='), ua)

    sign_params = {
        "X-Bogus": params['X-Bogus'],
        "aid": "6383",
        "app_name": "douyin_web",
        "browser_language": "zh-CN",
        "browser_name": "Edge",
        "browser_platform": "Win32",
        "browser_version": "118.0.2088.61",
        "content": msg,
        "cookie_enabled": "true",
        "device_platform": "web",
        "language": "zh-CN",
        "live_id": "1",
         "room_id": "7293676729145608999",
        "screen_height": "1080",
        "screen_width": "1920",
        "type": "0",
        "pathname": "/webcast/room/chat/",
        "tt_webid": "",
        "uuid": ""
    }
    host = "live.douyin.com/623302353683"
    tt_scid = cookies['tt_scid']
    params['_signature'] = get_ac_signatuer(urllib.parse.urlencode(sign_params).replace('%2F', '/').replace('%3D', '='), ua, host, tt_scid)

    print(params)
    print(cookies)
    response = requests.get(url, headers=headers, cookies=cookies, params=params)

    if response.json()['status_code'] == 0:
        print(f'发送成功：{response.json()["data"]["msg_id"]}')
    else:
        print(response.json())
        print('发送失败')


if __name__ == '__main__':
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.61"
    # send_msg(f'不能看到我', ua)
    for i in range(10):
        text = fake.paragraph()
        send_msg(f'{text}', ua)
        print(text)
        time.sleep(30)