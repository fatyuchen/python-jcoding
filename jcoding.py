# -*- coding:utf-8 -*-
u'''
Created on 2014年12月14日
功能：通用字符编码处理
处理方法介绍：
    1、如已经安装chardet，则会尝试由chardet检测字符编码；
    2、如未安装chardet则完全由__PriorityCoding__说设置的字符编码尝试解码，优先级就是__PriorityCoding__的元素顺序；
    3、首先由chardet探测字符编码，如大于等于__ChardetThreshold__且未出现在__ChardetException__中，则尝试采用探测到的字符编码解码；
    4、chardet探测到的字符编码如出现在__ChardetMapping__的key中，则转换成key对应的value；
    5、如按chardet探测到的字符编码解码失败，则由__PriorityCoding__按顺序解码；
    6、如上述方法均解码失败，则由chardet探测到的字符编码解码，不论可信度多少；
    7、如均告失败，则报错：Decoding failure
@author: 雨辰,fatyuchen@qq.com
'''
try:
    import chardet
    __UsingChardet__ = True
except ImportError:
    __UsingChardet__ = False

__author__ = 'fatyuchen <fatyuchen@qq.com>'
__version__ = '0.0.1'
__PriorityCoding__ = ('utf8','gb2312','gbk','big5')
__ChardetMapping__ = {
             'UTF-16LE':'utf16',
             'UTF-16BE':'utf16',
             'UTF-32LE':'utf32',
             }
__ChardetException__ = ('ISO-8859-7','ISO-8859-5','windows-1252')
__ChardetThreshold__ = 0.99 #信任chardet字符编码判断的阀值

def __isCoding(coding,s):
    u'''
    :判断是否可以按指定coding解码
    '''
    if not isinstance(s,str):
        return False
    try:
        s.decode(coding)
    except:
        return False
    return True
def __detect(s,threshold):
    u'''
    :测试s的字符编码
    '''
    global __UsingChardet__ , __ChardetMapping__ , __ChardetException__
    if not __UsingChardet__:
        return None
    if not isinstance(s,str):
        return None
    try:
        result = chardet.detect(s)
    except:
        return None
    if result['confidence'] < threshold:
        return None
    coding = result['encoding']
    if __ChardetMapping__.has_key(coding):
        coding = __ChardetMapping__[coding]
    try:
        s.decode(coding)
    except:
        return None
    try:
        __ChardetException__.index(coding)
    except:
        return coding
    return None
def __toUnicode(s):
    u'''
    :得到s的unicode编码
    :参数s:可以是字符串、tuple、set、list、dict
    '''
    global __ChardetThreshold__ , __PriorityCoding__
    if isinstance(s,dict):
        rtn = {}
        for k,v in s.items():
            rtn[k] = __toUnicode(v)
        return rtn
    if isinstance(s,list):
        rtn = []
        for v in s:
            rtn.append(__toUnicode(v))
        return rtn
    if isinstance(s,tuple):
        rtn = ()
        for v in s:
            rtn = rtn + (__toUnicode(v),)
        return rtn
    if isinstance(s,set):
        rtn = set()
        for v in s:
            rtn.add(__toUnicode(v))
        return rtn
    if not isinstance(s,str) and not isinstance(s,unicode):
        return s
    if isinstance(s,unicode):
        try:
            s.encode('raw_unicode_escape')
        except:
            return s
        if len(s) == len(s.encode('raw_unicode_escape')):
            s = s.encode('raw_unicode_escape')
        else:
            return s
    detect = __detect(s,__ChardetThreshold__)
    if detect is None:
        for c in __PriorityCoding__:
            if __isCoding(c,s):
                return s.decode(c)
    else:
        try:
            return s.decode(detect)
        except:
            pass
    detect = __detect(s,0)
    if detect is not None:
        try:
            return s.decode(detect)
        except:
            pass
    raise ValueError("Decoding failure")
def toUnicode(*args,**kwargs):
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
    if len(args) > 0:
        _args = __toUnicode(args)
    else:
        _args = ()
    if len(kwargs) > 0:
        _kwargs = __toUnicode(kwargs)
    else:
        _kwargs = {}
    if len(_args) == 0 and len(_kwargs) == 0:
        return None
    if len(_args) == 0:
        return _kwargs
    if len(_kwargs) == 0:
        if len(_args) > 1:
            return _args
        else:
            return _args[0]
    return _args,_kwargs
def __encoding(encoding,s):
    u'''
    :将s编码为指定coding
    :参数
    :coding:指定字符编码
    :s:可以是字符串、tuple、set、list、dict
    '''
    if isinstance(s,dict):
        rtn = {}
        for k,v in s.items():
            rtn[k] = __encoding(encoding,v)
        return rtn
    if isinstance(s,list):
        rtn = []
        for v in s:
            rtn.append(__encoding(encoding,v))
        return rtn
    if isinstance(s,tuple):
        rtn = ()
        for v in s:
            rtn = rtn + (__encoding(encoding,v),)
        return rtn
    if isinstance(s,set):
        rtn = set()
        for v in s:
            rtn.add(__encoding(encoding,v))
        return rtn
    if not isinstance(s,str) and not isinstance(s,unicode):
        return s
    return __toUnicode(s).encode(encoding,'ignore')
def encoding(encoding='',*args,**kwargs):
    u'''
    :coding:指定的字符编码
    :将args元组的各个字符型值全部转换为指定coding，将kwargs的各个字符型值转换为指定coding
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
    if len(args) > 0:
        _args = __encoding(encoding,args)
    else:
        _args = ()
    if len(kwargs) > 0:
        _kwargs = __encoding(encoding,kwargs)
    else:
        _kwargs = {}
    if len(_args) == 0 and len(_kwargs) == 0:
        return None
    if len(_args) == 0:
        return _kwargs
    if len(_kwargs) == 0:
        if len(_args) > 1:
            return _args
        else:
            return _args[0]
    return _args,_kwargs
def toGb2312(*args,**kwargs):
    u'''
    :将args元组的各个字符型值全部转换为gb2312，将kwargs的各个字符型值转换为gb2312
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
    return encoding('gb2312',*args,**kwargs)
def toGbk(*args,**kwargs):
    u'''
    :将args元组的各个字符型值全部转换为gbk，将kwargs的各个字符型值转换为gbk
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
    return encoding('gbk',*args,**kwargs)
def toUtf8(*args,**kwargs):
    u'''
    :将args元组的各个字符型值全部转换为utf8，将kwargs的各个字符型值转换为utf8
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
    return encoding('utf8',*args,**kwargs)