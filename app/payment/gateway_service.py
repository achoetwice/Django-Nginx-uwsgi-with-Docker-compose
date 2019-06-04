from Crypto.Cipher import AES
import urllib.parse
import binascii
import hashlib
import json, string

def strip_unprintable(data):
    return ''.join(c for c in data if c in string.printable)

def AES_encrypt(data, key, iv):
    cryptor = AES.new(key, AES.MODE_CBC, iv)
    return cryptor.encrypt(data)

def AES_decrypt(data, key, iv):
    cryptor = AES.new(key, AES.MODE_CBC, iv)
    return cryptor.decrypt(data)

def NEWEBPAY_AES(order_params, key, iv):
    # parameter to url query string
    order_params = urllib.parse.urlencode(order_params)
    # print ('order_params', order_params)
    # parameter padding, AES256 encode
    BS = 32
    pad_params = order_params + (BS - len(order_params) % BS) * chr(BS - len(order_params) % BS)
    AES_info = AES_encrypt(pad_params, key, iv)
    # print ('AES_info', AES_info)
    AES_info_str = str(binascii.hexlify(AES_info), 'ascii')
    # print ('AES_info_str', AES_info_str)
    return AES_info_str

def NEWEBPAY_SHA(AES_plus):
    m = hashlib.sha256()
    m.update(AES_plus.encode('ascii'))
    SHA_info = m.digest()
    SHA_info_str = str(binascii.hexlify(SHA_info), 'ascii')
    SHA_info_STR = SHA_info_str.upper()
    # print ('SHA_info_STR', SHA_info_STR)
    return SHA_info_STR
    
def NEWEBPAY_AES_decrypt(AES_info_str, key, iv):
    AES_info = AES_info_str.encode('utf-8')
    AES_info = binascii.unhexlify(AES_info)
    AES_info = AES_decrypt(AES_info, key, iv)
    AES_info = str(AES_info, 'ascii')
    AES_info = eval(strip_unprintable(AES_info))
    # print ('AES_info2', AES_info)
    return (AES_info)
