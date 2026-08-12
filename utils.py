#
#   utils.py
#

import json
import sys
import re

#
#   2.4GHz channel sets (20/40MHz)
#
chlist2G = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14']
chsets2G = {}

for i in range(14): # 1 - 14
    chsets2G[chlist2G[i]] = set(chlist2G[max(i-2, 0):min(i+3, len(chlist2G))])

for i in range(9):  # 1+ - 9+
    chsets2G[chlist2G[i]+'+'] = set(chlist2G[max(i-2, 0):min(i+8, len(chlist2G))])

for i in range(5,14):   # 6- - 14-
    chsets2G[chlist2G[i]+'-'] = set(chlist2G[max(i-7, 0):min(i+3, len(chlist2G))])


#
#   5GHz channel sets (20/40/80/160MHz)
#
chlist = ['36', '40', '44', '48', '52', '56', '60', '64',       # U-NII-1, U-NII-2A
           '100', '104', '108', '112', '116', '120', '124', '128', '132', '136', '140', '144',  # U-NII-2e
             '149', '153', '157', '161', '165'  # U-NII-3
             ]
chlist40 = ['36', '44', '52', '60', '100', '108', '116', '124', '132', '140', '149', '157']
chlist80 = ['36', '52', '100', '116', '132', '149']
chlist160 = ['36', '100']
chsets5G = {}

for ch in chlist:
    chsets5G[ch] = {ch}
for ch in chlist40:
    ch2 = str(int(ch)+4)
    chset = {ch, ch2}
    chsets5G[ch  + '+'] = chset
    chsets5G[ch2 + '-'] = chset
for ch in chlist80:
    ch2 = str(int(ch)+4)
    ch3 = str(int(ch)+8)
    ch4 = str(int(ch)+12)
    chset = {ch, ch2, ch3, ch4}
    chsets5G[ch  + 'E'] = chset
    chsets5G[ch2 + 'E'] = chset
    chsets5G[ch3 + 'E'] = chset
    chsets5G[ch4 + 'E'] = chset
for ch in chlist160:
    ch2 = str(int(ch)+4)
    ch3 = str(int(ch)+8)
    ch4 = str(int(ch)+12)
    ch5 = str(int(ch)+16)
    ch6 = str(int(ch)+20)
    ch7 = str(int(ch)+24)
    ch8 = str(int(ch)+28)
    chset = {ch, ch2, ch3, ch4, ch5, ch6, ch7, ch8}
    chsets5G[ch  + 'S'] = chset
    chsets5G[ch2 + 'S'] = chset
    chsets5G[ch3 + 'S'] = chset
    chsets5G[ch4 + 'S'] = chset
    chsets5G[ch5 + 'S'] = chset
    chsets5G[ch6 + 'S'] = chset
    chsets5G[ch7 + 'S'] = chset
    chsets5G[ch8 + 'S'] = chset

#
#   6GHz channel sets (20/40/80/160MHz)
#
chlist_6G = ['1', '5', '9', '13', '17', '21', '25', '29', '33', '37', '41', '45', '49', '53', '57', '61', '65', '69', '73', '77', '81', '85', '89', '93']
chsets6G = {}

for ch in chlist_6G:
    chsets6G[ch] = {ch}
for i in range(0, len(chlist_6G), 2):
    ch1 = chlist_6G[i]
    ch2 = chlist_6G[i+1]
    chsets6G[ch1 + '+'] = {ch1, ch2}
    chsets6G[ch2 + '-'] = {ch1, ch2}
for i in range(0, len(chlist_6G), 4):
    chset = set(chlist_6G[i:i+4])
    ch2 = chlist_6G[i+1]    # PSC channel
    chsets6G[ch2 + 'E'] = chset
for i in range(0, len(chlist_6G), 8):
    chset = set(chlist_6G[i:i+8])
    ch2 = chlist_6G[i+1]    # PSC channel
    ch6 = chlist_6G[i+5]    # PSC channel
    chsets6G[ch2 + 'S'] = chset
    chsets6G[ch6 + 'S'] = chset



def isintf(band, ch1, ch2):
    """ch1 と ch2 が干渉するかどうかを判定する。干渉する場合は True を返す。"""
    if band == '2':
        if ch1 not in chsets2G:
            raise ValueError(f"Unknown 2.4GHz channel: {ch1}")
        if ch2 not in chsets2G:
            raise ValueError(f"Unknown 2.4GHz channel: {ch2}")
        return bool(chsets2G[ch1] & chsets2G[ch2])
    elif band == '5':
        if ch1 not in chsets5G:
            raise ValueError(f"Unknown 5GHz channel: {ch1}")
        if ch2 not in chsets5G:
            raise ValueError(f"Unknown 5GHz channel: {ch2}")
        return bool(chsets5G[ch1] & chsets5G[ch2])
    elif band == '6':
        if ch1 not in chsets6G:
            raise ValueError(f"Unknown 6GHz channel: {ch1}")
        if ch2 not in chsets6G:
            raise ValueError(f"Unknown 6GHz channel: {ch2}")
        return bool(chsets6G[ch1] & chsets6G[ch2])
    else:
        raise ValueError(f"Unknown band: {band}")


def _object_attrs(obj):
    """クラスオブジェクトの属性を dict で返す。属性を持たない場合は None。"""
    if isinstance(obj, type) or callable(obj):
        return None
    attrs = getattr(obj, '__dict__', None)
    if isinstance(attrs, dict):
        return dict(attrs)
    slots = getattr(obj, '__slots__', None)
    if slots is not None:
        if isinstance(slots, str):
            slots = [slots]
        return {name: getattr(obj, name) for name in slots if hasattr(obj, name)}
    return None


CYAN = '\033[36m'
YELLOW = '\033[33m'
RESET = '\033[0m'


def _paint(text, color, enabled):
    return f'{color}{text}{RESET}' if enabled else text


def format_value(value, level=0, indent=4, seen=None, color=True):
    """値を json.dumps() 風にインデント・改行した文字列に整形する。"""
    seen = set() if seen is None else seen
    pad = ' ' * (indent * level)
    inner_pad = ' ' * (indent * (level + 1))

    def block(open_str, entries, close_str):
        if not entries:
            return open_str + close_str
        body = ',\n'.join(inner_pad + e for e in entries)
        return f'{open_str}\n{body}\n{pad}{close_str}'

    def key_value(k, v):
        key = _paint(json.dumps(str(k), ensure_ascii=False), YELLOW, color)
        return f'{key}: {format_value(v, level + 1, indent, seen, color)}'

    if isinstance(value, (str, bytes, bytearray)) or value is None or isinstance(value, (int, float)):
        # 文字列・数値・真偽値・None はそのまま JSON リテラルとして出力
        if isinstance(value, (bytes, bytearray)):
            return json.dumps(str(value), ensure_ascii=False)
        return json.dumps(value, ensure_ascii=False)

    if id(value) in seen:
        return '"<circular reference>"'
    seen = seen | {id(value)}

    if isinstance(value, dict):
        return block('{', [key_value(k, v) for k, v in value.items()], '}')

    if isinstance(value, (list, tuple, set, frozenset)):
        entries = [format_value(v, level + 1, indent, seen, color) for v in value]
        return block('[', entries, ']')

    attrs = _object_attrs(value)
    if attrs is not None:
        cls = type(value).__name__
        return block(
            _paint(f'{cls} (', CYAN, color),
            [key_value(k, v) for k, v in attrs.items()],
            _paint(f')  // {cls}', CYAN, color),
        )

    return json.dumps(str(value), ensure_ascii=False)


def print_dict(d, indent=4, color=None):
    # color=None なら端末出力のときだけ色付けする
    if color is None:
        color = sys.stdout.isatty()
    print(format_value(d, indent=indent, color=color))


def bytes_to_str(num_bytes, suffix='B'):
    """
    Convert a number of bytes to a human-readable string format (e.g., KB, MB, GB).
    
    :param num_bytes: Number of bytes to convert.
    :return: A string representing the size in a human-readable format.
    """
    if num_bytes is None:
        return 'n/a'

    if not isinstance(num_bytes, (int, float)):
        return(str(num_bytes))

    if num_bytes < 1024:
        if suffix:
            return f"{num_bytes} {suffix}"
        return f"{num_bytes}"

    num_bytes /= 1024.0
    for unit in ['K', 'M', 'G']:
        if num_bytes < 1024.0:
            return f"{num_bytes:.2f} {unit}{suffix}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} T{suffix}"


def sec2str(seconds):
    """
    Convert seconds to a human-readable string format (days, hours, minutes, seconds).
    
    :param seconds: Number of seconds to convert.
    :return: A string representing the time in days, hours, minutes, and seconds.
    """
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{days}d {hours}h {minutes}m {secs}s"


def normalize_mac(s):
    """
    Normalize a MAC address string to the format 'xx:xx:xx:xx:xx:xx'.
    
    :param s: MAC address string in various formats (e.g., 'AA-BB-CC-DD-EE-FF', 'AABB.CCDD.EEFF', 'AABBCCDDEEFF').
    :return: Normalized MAC address string in the format 'xx:xx:xx:xx:xx:xx'.
    """
    # Remove any non-hexadecimal characters
    s = re.sub(r'[^0-9a-fA-F]', '', s)
    # Ensure the string has exactly 12 hexadecimal characters
    if len(s) != 12:
        return None
    # Format the string into the standard MAC address format
    return ':'.join(s[i:i+2] for i in range(0, 12, 2)).lower()

