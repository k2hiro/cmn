#
#   utils.py
#

import json
import sys
import re

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

