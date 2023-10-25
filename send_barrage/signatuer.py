import base64
import ctypes
import random
import time


def _0x49c5cb(a, c):
    b = len(a)
    d = b >> 2
    if 0 != (3 & b):
        d += 1
    if c:
        e = [0] * (d + 1)
        e[d] = b
    else:
        e = [0] * d

    for c in range(b):
        e[c >> 2] |= ord(a[c]) << ((3 & c) << 3)

    return e


def _0x25913f(a):
    return 4294967295 & a



def _0x3dd1d4(a, c, e, b, d, f):
    # 模拟 JavaScript 中的 >>> 无符号右移操作
    e = ctypes.c_uint32(e).value
    c = ctypes.c_uint32(c).value

    result = ((e >> 5) ^ (c << 2)) + ((c >> 3) ^ (e << 4)) ^ (a.value ^ c) + (f[3 & b ^ d] ^ e)

    return result



def _0x5129a4(a, c):
    o = len(a)
    i = o - 1
    b = a[i]
    d = 0
    n = int(6 + 52 / o)
    _0x228885 = 2654435769
    for _ in range(n):
        if type(d) == ctypes.c_ulong:
            d = d.value
        d = _0x25913f(d + _0x228885)
        d = ctypes.c_uint32(d)
        f = (d.value >> 2) & 3

        for t in range(i):
            e = a[t + 1]
            b = a[t] = _0x25913f(a[t] + _0x3dd1d4(d, e, b, t, f, c))

        e = a[0]
        b = a[i] = _0x25913f(a[i] + _0x3dd1d4(d, e, b, i, f, c))

    return a



def _0x262b9d(a, c):
    e = len(a)
    b = e << 2

    if c:
        d = a[e - 1]
        b -= 4
        if d < (b - 3) or d > b:
            return None
        b = d

    # for f in range(e):
    #     num1 = ctypes.c_uint32(a[f])
    #     num1.value >>= 8
    #
    #     num2 = ctypes.c_uint32(a[f])
    #     num2.value >>= 16
    #
    #     num3 = ctypes.c_uint32(a[f])
    #     num3.value >>= 24
    #     print(255 & a[f], num1.value & 255, num2.value & 255, num3.value & 255)
    #     a[f] = chr(255 & a[f]) + chr(num1.value & 255) + chr(num2.value & 255) + chr(num3.value & 255)
    for f in range(e):
        num = ctypes.c_uint32(a[f])
        a[f] = chr(255 & a[f]) + chr((num.value >> 8) & 255) + chr((num.value >> 16) & 255) + chr((num.value >> 24) & 255)
    t = "".join(a)
    return t[:b] if c else t


def _0x484d1f(a):
    if len(a) < 4:
        a += [0] * (4 - len(a))
    return a



def _0xf864b4(a, c, e=None):
    b = "Dkdpgh4ZKsQB80/Mfvw36XI1R25+WUAlEi7NLboqYTOPuzmFjJnryx9HVGcaStCe"
    d = "="
    if e:
        d = ""
    if c:
        b = c

    t = ""
    n = 0
    while len(a) >= n + 3:
        f = (255 & ord(a[n])) << 16 | (255 & ord(a[n+1])) << 8 | (255 & ord(a[n+2]))
        t += b[(16515072 & f) >> 18]
        t += b[(258048 & f) >> 12]
        t += b[(4032 & f) >> 6]
        t += b[63 & f]
        n += 3

    if len(a) - n > 0:
        f = (255 & ord(a[n])) << 16
        if len(a) > n+1:
            f |= (255 & ord(a[n+1])) << 8
        t += b[(16515072 & f) >> 18]
        t += b[(258048 & f) >> 12]
        if len(a) > n+1:
            t += b[(4032 & f) >> 6]
        else:
            t += d
        t += d

    return t



def _0x3083ae(a, c=None):
    if not c:
        c = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    e = ""
    for b in range(a):
        e += random.choice(c)
    return e


def enc_ttscid(ttscid):
    ttscid_key = _0x3083ae(4)
    # ttscid_key = "b0ok"
    return ttscid_key + _0xf864b4(_0x262b9d(_0x5129a4(_0x49c5cb(ttscid, 1), _0x484d1f(_0x49c5cb(ttscid_key, 0))), 0), "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-.")


def unsinged_right_shift(x, y):
    """
    无符号右移
    :param x:
    :param y:
    :return:
    """
    x = x & 0xffffffff
    signed = False
    if x < 0:
        signed = True
    x = x.to_bytes(4, byteorder='big', signed=signed)  # 有符号
    x = int.from_bytes(x, byteorder='big', signed=False)  # 无符号
    return x >> (y & 0xf)


def enc1(data, temp):
    for index, value in enumerate(str(data)):
        temp = unsinged_right_shift((temp ^ ord(value)) * 65599, 0)

    return temp


def get_ac_signatuer(data, ua, host, tt_scid, canvas=536919696):
    """
    :param data:
    :param ua:
    :param canvas:
    :return:
    """
    s = int(time.time())
    enc_time = enc1(s, 0)

    enc_host = enc1(host, enc_time)

    enc_time_host = int('10000000110000' + bin(unsinged_right_shift(s ^ enc_host % 65521 * 65521, 0))[2:].zfill(32), 2)
    # print("enc_time_host", enc_time_host)
    _signature = ''

    # 1-5
    enc_time_host_int32 = ctypes.c_int32(enc_time_host)
    enc_time_host_int32.value >>= 2
    for _ in range(4, -1, -1):
        chr1 = enc_time_host_int32.value >> (_ * 6) & 63
        if chr1 >= 62:
            _signature += chr(chr1 - 17)
        elif chr1 >= 52:
            _signature += chr(chr1 - 4)
        elif chr1 >= 26:
            _signature += chr(chr1 + 71)
        else:
            _signature += chr(chr1 + 65)

    # 6-10
    temp1 = int(enc_time_host / 4294967296)
    temp2 = ctypes.c_int32(temp1).value >> 4
    enc_time_host_int32 = ctypes.c_int32(enc_time_host)
    enc_time_host_int32.value <<= 28
    temp3 = enc_time_host_int32.value ^ temp2
    for _ in range(4, -1, -1):
        chr1 = temp3 >> (_ * 6) & 63
        if chr1 >= 62:
            _signature += chr(chr1 - 17)
        elif chr1 >= 52:
            _signature += chr(chr1 - 4)
        elif chr1 >= 26:
            _signature += chr(chr1 + 71)
        else:
            _signature += chr(chr1 + 65)

    # 11-15
    temp4 = ctypes.c_int32(temp1)
    temp4.value <<= 26
    temp5 = temp4.value ^ unsinged_right_shift((canvas ^ enc_time_host), 6)
    for _ in range(4, -1, -1):
        chr1 = temp5 >> (_ * 6) & 63
        if chr1 >= 62:
            _signature += chr(chr1 - 17)
        elif chr1 >= 52:
            _signature += chr(chr1 - 4)
        elif chr1 >= 26:
            _signature += chr(chr1 + 71)
        else:
            _signature += chr(chr1 + 65)

    # 16
    chr1 = (canvas ^ enc_time_host) & 63
    if chr1 >= 62:
        _signature += chr(chr1 - 17)
    elif chr1 >= 52:
        _signature += chr(chr1 - 4)
    elif chr1 >= 26:
        _signature += chr(chr1 + 71)
    else:
        _signature += chr(chr1 + 65)

    # 17-21
    enc_data = enc1(data, enc1(enc_time_host, 0))
    enc_ua = enc1(ua, enc1(enc_time_host, 0))
    temp6 = ctypes.c_int32(enc_ua % 65521)
    temp6.value <<= 16
    temp7 = ctypes.c_int32(temp6.value ^ (enc_data % 65521))
    temp7.value >>= 2
    for _ in range(4, -1, -1):
        chr1 = temp7.value >> (_ * 6) & 63
        if chr1 >= 62:
            _signature += chr(chr1 - 17)
        elif chr1 >= 52:
            _signature += chr(chr1 - 4)
        elif chr1 >= 26:
            _signature += chr(chr1 + 71)
        else:
            _signature += chr(chr1 + 65)
    # 22-26
    temp8 = ctypes.c_int32(temp6.value ^ (enc_data % 65521))
    temp8.value <<= 28
    # temp9 = unsinged_right_shift(((((1 << 11) + 1) << 8) | 32) ^ enc_time_host, 4)  # 视频接口
    temp9 = unsinged_right_shift(((1 << 8) | 32) ^ enc_time_host, 4)  # 抖币充值接口
    # temp9 = unsinged_right_shift(65824 ^ enc_time_host, 4)  # 创作者中心
    temp10 = temp8.value ^ temp9
    for _ in range(4, -1, -1):
        chr1 = temp10 >> (_ * 6) & 63
        if chr1 >= 62:
            _signature += chr(chr1 - 17)
        elif chr1 >= 52:
            _signature += chr(chr1 - 4)
        elif chr1 >= 26:
            _signature += chr(chr1 + 71)
        else:
            _signature += chr(chr1 + 65)
    # 27-31
    temp11 = enc_host % 65521
    for _ in range(4, -1, -1):
        chr1 = temp11 >> (_ * 6) & 63
        if chr1 >= 62:
            _signature += chr(chr1 - 17)
        elif chr1 >= 52:
            _signature += chr(chr1 - 4)
        elif chr1 >= 26:
            _signature += chr(chr1 + 71)
        else:
            _signature += chr(chr1 + 65)

    # print("_signature", _signature)
    temp12 = 0
    _signature = _signature + enc_ttscid(tt_scid)
    temp13 = '_02B4Z6wo00001' + _signature
    for index, value in enumerate(temp13):
        temp12 = unsinged_right_shift(((temp12 * 65599) + ord(value)), 0)

    _signature = '_02B4Z6wo00001' + _signature + hex(temp12)[-2:]

    return _signature


if __name__ == '__main__':


    # canvas = 1489154074  # canvas指纹
    # data = 'pathname=/web/api/media/anchor/search&tt_webid=&uuid='
    # ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36 Edg/100.0.1185.29"
    # host = "creator.douyin.com/creator-micro/home"
    #
    # tt_scid = "WGD0XOJTkExG8nwiltsJOjQJ7xIyGANyLdlp4OphyzGJLwJmrwUVv-mX1cuD-gQ69fde"


    canvas = 536919696  # canvas指纹
    data = "X-Bogus=DFSzswVLCt0ANxJAtY/JkM9WX7rn&aid=6383&app_name=douyin_web&browser_language=zh-CN&browser_name=Chrome&browser_platform=Win32&browser_version=103.0.0.0&content=1234&cookie_enabled=true&device_platform=web&language=zh-CN&live_id=1&msToken=00YBZLIupBr49j1-5KxMq6npc3-YdlBeB-qpPL2YVVe-VQdjd8vxm8wh9ZLDuqdv-La-SwEC95RLEeYrRATH4uHAuL54TyVgBo0TWK7UPk6F6eiAjpu9nje6wJoI&room_id=7293402264545282816&screen_height=1080&screen_width=1920&type=0&pathname=/webcast/room/chat/&tt_webid=&uuid="


    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    host = "live.douyin.com/276821963405"

    tt_scid = "85SmCiuFol7tVMDWgA-itM48Wkz6ScdT2KCQx5BI-6gk0bAkbqCRuPcB10m89uz-f116"
    print(get_ac_signatuer(data, ua, canvas))

