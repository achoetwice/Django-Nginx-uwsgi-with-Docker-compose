from helper.helper import APIHandler
from django.db import transaction
from decimal import Decimal
import time
from payment.gateway_service import *

def CREATE_B2C_PAPER_INVOICE(data):
    item_count = int(data['ItemCount'])
    item_price = int(data['ItemPrice'])
    item_amt = item_count * item_price
    tax_amt_raw = item_amt*0.05
    tax_amt = Decimal(f'{tax_amt_raw}').quantize(Decimal('1.'), rounding=ROUND_HALF_UP)
    total_amt = item_amt + tax_amt

    order_params={
        'RespondType': 'JSON',
        'Version': '1.4',
        'TimeStamp': f'{int(time.time())}',
        'MerchantOrderNo': data['MerchantOrderNo'],
        'Status': '1', # 1=即時開立
        # 'CreateStatusTime' 預設開立日期
        'Category': 'B2C',  # B2B or B2C
        'BuyerName': data['BuyerName'],  # Customer name
        # 'BuyerAddress': data['customer_address']
        'BuyerEmail': data['BuyerEmail'],  # Customer email
        'PrintFlag': 'Y', # Y=索取發票
        'ItemName': data['ItemName'], # 單項：商品一  多項：商品一｜商品二｜...
        'ItemCount': item_count, # 商品數量，多項模式同itemname
        'ItemUnit': data['ItemUnit'], #商品單位
        'ItemPrice': item_price, #商品單價
        'ItemAmt ': item_amt,#數量*單價
        'TaxType':'1', # 1=應稅
        'TaxRate':5, # 5為一般稅率
        'Amt': item_amt,# 銷售金額
        'TaxAmt': tax_amt, # 銷售金額的5%
        'TotalAmt': total_amt, # Amt + TaxAmt
        'Comment': data['Card4No'] #信用卡末四碼：1234
    }
