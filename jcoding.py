# -*- coding:utf-8 -*-
u'''
Created on 2014年12月14日
功能：通用字符编码处理
处理方法介绍：
    1、如已经安装chardet，则会尝试由chardet检测字符编码；
    2、如未安装chardet则完全由PRIORITY_CODING说设置的字符编码尝试解码，
                    优先级就是PRIORITY_CODING的元素顺序；
    3、首先由chardet探测字符编码，如大于等于CHARDET_THRESHLOD
                    且未出现在CHARDET_EXCEPTION中，则尝试采用探测到的字符编码解码；
    4、chardet探测到的字符编码如出现在CHARDET_MAPPING的key中，则转换成key对应的value；
    5、如按chardet探测到的字符编码解码失败，则由PRIORITY_CODING按顺序解码；
    6、如上述方法均解码失败，则由chardet探测到的字符编码解码，不论可信度多少；
    7、如均告失败，则报错：Decoding failure
@author: 雨辰,fatyuchen@qq.com
'''
try:
    import chardet
    USING_CHARDET = True
except ImportError:
    USING_CHARDET = False

__author__ = 'fatyuchen <fatyuchen@qq.com>'
__version__ = '0.0.1'

# 优先判定字符编码
PRIORITY_CODING = ('utf8', 'gb2312', 'gbk', 'big5')

# chardet判定映射
CHARDET_MAPPING = {'UTF-16LE': 'utf16',
                   'UTF-16BE': 'utf16',
                   'UTF-32LE': 'utf32'}

# 不信任chardet判定列表
CHARDET_EXCEPTION = ('ISO-8859-7', 'ISO-8859-5', 'windows-1252')

# 信任chardet字符编码判断的阀值
CHARDET_THRESHLOD = 0.99


def _isencoding(encoding, s):
    u'''
    :判断是否可以按指定coding解码
    '''
    if not isinstance(s, str):
        return False
    try:
        s.decode(encoding)
    except:
        return False
    return True


def _detect(s, threshold):
    u'''
    :测试s的字符编码,可信度必须大于等于threshold。
    '''
    if not USING_CHARDET:
        return None
    if not isinstance(s, str):
        return None
    try:
        result = chardet.detect(s)
    except:
        return None
    if result['confidence'] < threshold:
        return None
    coding = result['encoding']
    if coding in CHARDET_MAPPING.keys():
        coding = CHARDET_MAPPING[coding]
    try:
        s.decode(coding)
    except:
        return None
    if coding not in CHARDET_EXCEPTION:
        return coding
    return None


def _tounicode(s):
    u'''
    :得到s的unicode编码
    :参数s:可以是字符串、tuple、set、list、dict
    '''
    if isinstance(s, dict):
        return dict((k, _tounicode(v)) for k, v in s.items())
    if isinstance(s, list):
        return list(_tounicode(v) for v in s)
    if isinstance(s, tuple):
        return tuple(_tounicode(v) for v in s)
    if isinstance(s, set):
        return set(_tounicode(v) for v in s)
    if not isinstance(s, str) and not isinstance(s, unicode):
        return s
    if isinstance(s, unicode):
        try:
            s.encode('raw_unicode_escape')
        except:
            return s
        if len(s) == len(s.encode('raw_unicode_escape')):
            s = s.encode('raw_unicode_escape')
        else:
            return s
    detect = _detect(s, CHARDET_THRESHLOD)
    if not detect:
        for c in PRIORITY_CODING:
            if _isencoding(c, s):
                return s.decode(c)
    else:
        try:
            return s.decode(detect)
        except:
            pass
    detect = _detect(s, 0)
    if detect:
        try:
            return s.decode(detect)
        except:
            pass
    raise ValueError("Decoding failure")


def toUnicode(*args, **kwargs):
    u'''
    :将args元组的各个字符型值全部转换为unicode，将kwargs的各个字符型值转换为unicode
    :如无kwargs则只返回args,类型为:tuple
    :如无args则只返回kwargs,类型为:dict
    :返回值:
    :   一般情况返回tuple和dict
    :   如无任何参数，返回None
    :   如无args，则只返回dict
    :   如无kwargs则根据args的个数决定如何返回：
    :        如args个数大于1，返回tuple
    :         args个数等于1，直接返回单值
    '''
    if args:
        _args = _tounicode(args)
    else:
        _args = ()
    if kwargs:
        _kwargs = _tounicode(kwargs)
    else:
        _kwargs = {}
    if not _args and not _kwargs:
        return None
    if not _args:
        return _kwargs
    if not _kwargs:
        if len(_args) > 1:
            return _args
        else:
            return _args[0]
    return _args, _kwargs


def _encoding(encoding, s):
    u'''
    :将s编码为指定encoding
    :参数
    :encoding:指定字符编码
    :s:可以是字符串、tuple、set、list、dict
    '''
    if isinstance(s, dict):
        return dict((k, _encoding(encoding, v)) for k, v in s.items())
    if isinstance(s, list):
        return list(_encoding(encoding, v) for v in s)
    if isinstance(s, tuple):
        return tuple(_encoding(encoding, v) for v in s)
    if isinstance(s, set):
        return set(_encoding(encoding, v) for v in s)
    if not isinstance(s, str) and not isinstance(s, unicode):
        return s
    return _tounicode(s).encode(encoding, 'ignore')


def encoding(encoding='', *args, **kwargs):
    u'''
    :encoding:指定的字符编码
    :将args元组的各个字符型值全部转换为指定encoding，将kwargs的各个字符型值转换为指定encoding
    :如无kwargs则只返回args,类型为:tuple
    :如无args则只返回kwargs,类型为:dict
    :返回值:
    :   一般情况返回tuple和dict
    :   如无任何参数，返回None
    :   如无args，则只返回dict
    :   如无kwargs则根据args的个数决定如何返回：
    :        如args个数大于1，返回tuple
    :         args个数等于1，直接返回单值
    '''
    if args:
        _args = _encoding(encoding, args)
    else:
        _args = ()
    if kwargs:
        _kwargs = _encoding(encoding, kwargs)
    else:
        _kwargs = {}
    if not _args and not _kwargs:
        return None
    if not _args:
        return _kwargs
    if not _kwargs:
        if len(_args) > 1:
            return _args
        else:
            return _args[0]
    return _args, _kwargs


def togbk(*args, **kwargs):
    u'''
    toGbk(*args,**kwargs) <==> encoding('gbk',*args,**kwargs)
    '''
    return encoding('gbk', *args, **kwargs)


def toutf8(*args, **kwargs):
    u'''
    toUtf8(*args,**kwargs) <==> encoding('utf8',*args,**kwargs)
    '''
    return encoding('utf8', *args, **kwargs)
