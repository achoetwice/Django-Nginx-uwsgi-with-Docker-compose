from .models import ClassSchedules, ClassOptions, ClassBranches, VendorClasses, VendorInfos, Transaction, GuestInfos, \
CountryLists, TransactionItems, VendorBranches, BookingClasses, BranchHistories, TransactionItemProfiles, GuestTemporaryInfo, TransactionCounterPay
from payment.serializers import *
from helper.helper import APIHandler
from datetime import datetime, date
import importlib.util
from copy import deepcopy
import pytz, json, os, uuid, time, pprint
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone
from .gateway_service import *
import requests

public_url = os.getenv('public_url')
public_url_sendmail = os.getenv('public_url_sendmail')

def StoreTempInfo(email, first_name, last_name, customer_mobile, learners, schedule_id, auto_create_account, guest_id):
    New_temp_info = GuestTemporaryInfo.objects.create(id =str(uuid.uuid4())[0:8], email = email, first_name = first_name, last_name = last_name, mobile = customer_mobile, \
    learners = learners, schedule_id = schedule_id, auto_create_account = auto_create_account, guest_id= guest_id)
    New_temp_info.save()
    return New_temp_info.id

def GetGuestTempInfo (temp_id):
    try:
        temp_info = GuestTemporaryInfo.objects.get(id = temp_id)
    except ObjectDoesNotExist:
        return ('')
    return temp_info

def GetClassInfo(schedule_id):
    schedule_id = schedule_id
    try:
        schedule = ClassSchedules.objects.get(pk= schedule_id)
    except ObjectDoesNotExist:
        return False
    # print ('schedule_vacancy', schedule.vacancy)
    option = schedule.option
    branch = option.branch
    classes = branch.classes
    vendor = classes.vendor
    data = {}
    data['schedule_name'] = schedule.schedule_name
    data['schedule_start_date'] = schedule.start_date
    # data['schedule_start_date_string'] = schedule.getStartDateString()
    data['schedule_end_date'] = schedule.end_date
    data['schedule_start_time'] = schedule.start_time
    data['schedule_end_time'] = schedule.end_time
    # data['schedule_time'] = schedule.class_time
    data['schedule_date_modified'] = schedule.updated_at
    data['vacancy'] = schedule.vacancy
    data['option_id'] = option.pk
    data['option_name'] = option.option_name
    data['option_date_modified'] = option.updated_at
    data['option_price'] = option.price
    data['price_prefix'] = option.price_prefix
    data['schedule_free_status'] = option.schedule_free_status
    data['branch_id'] = branch.pk
    data['branch_name'] = branch.class_branch
    data['branch_country'] = branch.country
    data['branch_city'] = branch.city
    data['branch_district'] = branch.district
    data['address'] = branch.address
    data['class_id'] = classes.pk
    data['class_name'] = classes.class_name
    data['class_date_modified'] = classes.updated_at
    data['vendor_id'] = vendor.pk
    data['vendor_name'] = vendor.vendor_name

    return data
        
# def CheckAgeValidation(learner, schedule_id):
#     try:
#         schedule = ClassSchedules.objects.get(pk= schedule_id)
#     except ClassSchedules.DoesNotExist:
#         return APIHandler("schedule not exist")
#     classes = schedule.option.branch.classes
#     birthday = datetime.strptime(learner['profile_dob'], '%Y/%m/%d')
#     class_date = schedule.start_date.replace(tzinfo=None)
#     time_diff = class_date - birthday
#     print (time_diff)
#     if classes.age_max == 'NULL' and classes.age_min == 'NULL':
#         return True
#     elif classes.age_max == 0 and classes.age_min == 0:
#         return True
#     elif classes.age_min == 'NULL':
#         age_min = 0
#     elif classes.age_max == 'NULL':
#         age_max = 999
#     else:
#         age_min = classes.age_min
#         age_max = classes.age_max
#     valid_age = age_max - age_min

#     age_year = time_diff.days // 365
#     age_month = time_diff.days % 365 //30

#     if age_min <= age_year <= age_max:
#         return True
#     elif age_min == 0 and age_max == 0:
#         return True
#     else:
#         return False

def SaveGuestInfos(email, first_name, last_name, customer_mobile):
    guest = GuestInfos()
    guest.email = email
    guest.first_name = first_name
    guest.last_name = last_name
    guest.mobile = customer_mobile
    guest.save()

    guest_id = GuestInfos.objects.latest('updated_at').id
    return guest_id

def GetGuestInfo(guest_id):
    guest_infos = GuestInfos.objects.get(id=guest_id)
    return guest_infos

def NEWEBPAY(schedule_id, learners, guest_id, temp_id):
    """
    MerchantID:藍新金流商店代號。
    TradeInfo:1.將交易資料參數（下方列表中參數）透過商店 Key 及 IV 進行 AES 加密。
    TradeSha:1.將交易資料經過上述 AES 加密過的字串，透過商店 Key 及 IV 進行 SHA256 加密。
    Version:請帶 1.5
    """
    schedule_id = schedule_id
    learners = learners
    class_info = GetClassInfo(schedule_id)
    #  Use int only because it's TWD
    sub_total = int(class_info['option_price'] * len(learners))
    item_name = class_info['option_name']
    guest_infos = GetGuestInfo(guest_id)

    # Better Use environment variable instead
    MerchantID = 'MS36244907'
    key = os.getenv('NEWEBPAY_KEY')
    iv = os.getenv('NEWEBPAY_IV')

    order_params = {
        'MerchantID': MerchantID,
        'RespondType': 'JSON',
        'TimeStamp': f'{int(time.time())}',
        'Version': '1.5',
        'LangType': 'zh-tw',
        'MerchantOrderNo': temp_id,
        'Amt': sub_total,
        'ItemDesc': item_name,
        'TradeLimit': 0, # 0 for no limit, use any int number 60~900 seconds as trade time limit 
        # 'ExpireDate': None,
        # 'ReturnURL': None, # 引導消費者返回商店
        'NotifyURL': public_url + '/payment/newebpay_return_data/', # 接收交易資訊
        # 'CustomerURL': None,
        # 'ClientBackURL': None, # 交易取消要去哪
        'Email':guest_infos.email, # 交易完成通知付款人（0.0）醬方便阿
        'EmailModify': 0,
        'LoginType': 0,
        # 'OrderComment': f'{id_dict}',
        'CREDIT': 1,
        # 'InstFlag': 0, # 分期功能
    }
    print ('order_params', order_params)
    
    # AES encode 
    AES_info_str = NEWEBPAY_AES(order_params, key, iv)

    # SHA256 encode
    AES_plus = 'HashKey=' + key + '&' + AES_info_str + '&' + 'HashIV=' + iv
    SHA_info_STR = NEWEBPAY_SHA(AES_plus)
    

    data = {
        'MerchantID':MerchantID,
        'TradeInfo':AES_info_str,
        'TradeSha':SHA_info_STR,
        'Version':'1.5'
    }
    # AES_info_str = '3a73f7942c2a61ea7e0c90b74ad704407fee1c844a6e33937767978219287296d4b816830a93c60a257d65076b0ab07c04d5712e260db25ecca41e5b5c6f9efa30ce99342a01aaaaa1ed528c1baea8de31a69e0d07436a4cc9f03f1064243684752dada60be524495a12b643bd59e7dfcf0ddf4ec26f4f537a90b751c24308fb8a3654855d401207a78745d2eabe6a81139fa2a4449deeabd6aedddf8672b0eb93dcc2dd6fb07544e54784e740eeab3a3eb6999d982f9d89e76b982d040b31f35a6c60d75ff9c704c5144bb9e4c818e564b06ff7487b9fbe3fef5532e95fbc4c5ed7fc5092accc98a80fb5af49b21bbe01db9dd4357572d8d7f51c0a7e75f39adb3a91d75896c5220cb4530da978f4a52c313878c047fc9ecc454e6b29fe28629a7d55ad600d07390177787b09808966b7e7a2b457bebe4a3c7b4c05117ec8fc093fb8e327f7231bbd6d3d896d26c23007065befcbd532f803db22865b2907e0521ceaf41c35d8cefdc34401c141b935958c5484e76bdbd1d76cd877daacb7439f9b1e9b3952c5ea9e9e24077d0f81b5a5bdd780e17494fc1ddfc61cb50e0713d7ecedc6733d24ce3e7c2a78b90e6b6b8c67d332b29a1a293a20680133ce88ec9d86f2612afee647ee276cf73bf0e16d6f9d014ca57eab253e78e14f73001bcc'
    # dec = NEWEBPAY_AES_decrypt(AES_info_str, key, iv)
    # dec = dec['Result']['MerchantOrderNo']
    # print ('decrypt', dec)

    return data

def NEWEBPAY_Decrypt(data):
    # Better Use environment variable instead
    key = os.getenv('NEWEBPAY_KEY')
    iv = os.getenv('NEWEBPAY_IV')
    AES_info = NEWEBPAY_AES_decrypt(data, key, iv)
    return AES_info


def ECPAY(schedule_id, learners, guest_id, temp_id):
    spec = importlib.util.spec_from_file_location(
        "ecpay_payment_sdk",
        "./sdk/ecpay_payment_sdk.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    schedule_id = schedule_id
    learners = learners
    class_info = GetClassInfo(schedule_id)
    #  Use int only because it's TWD
    sub_total = int(class_info['option_price'] * len(learners))
    item_name = class_info['option_name']
    order_params = {
        'MerchantTradeNo': datetime.now().strftime("EDPOS%Y%m%d%H%M%S"),
        'StoreID': '',
        'MerchantTradeDate': datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        'PaymentType': 'aio',
        'TotalAmount': sub_total,
        'TradeDesc': 'edpos_trade',
        'ItemName': item_name,
        # Go to Store tran
        'ReturnURL': public_url + '/payment/return_data/',
        'ChoosePayment': 'Credit',
        'ClientBackURL': public_url + '/payment/close_page/',
        'ItemURL': 'https://www.ecpay.com.tw/item_url.php',
        'Remark': '交易備註',
        'ChooseSubPayment': '',
        'OrderResultURL': '',
        'NeedExtraPaidInfo': 'Y',
        'DeviceSource': '',
        'IgnorePayment': '',
        'PlatformID': '',
        'InvoiceMark': 'N',
        'CustomField1': {'s_id':schedule_id},
        'CustomField2': {'g_id':guest_id},
        'CustomField3': {'t_id':temp_id},
        'CustomField4': '',
        # 'BindingCard' : 1,
        'EncryptType': 1,
    }

    extend_params_1 = {
        'BindingCard': 0,
        'MerchantMemberID': '',
    }

    extend_params_2 = {
        'Redeem': 'N',
        'UnionPay': 0,
    }

    inv_params = {
        # 'RelateNumber': 'Tea0001', # 特店自訂編號
        # 'CustomerID': 'TEA_0000001', # 客戶編號
        # 'CustomerIdentifier': '53348111', # 統一編號
        # 'CustomerName': '客戶名稱',
        # 'CustomerAddr': '客戶地址',
        # 'CustomerPhone': '0912345678', # 客戶手機號碼
        # 'CustomerEmail': 'abc@ecpay.com.tw',
        # 'ClearanceMark': '2', # 通關方式
        # 'TaxType': '1', # 課稅類別
        # 'CarruerType': '', # 載具類別
        # 'CarruerNum': '', # 載具編號
        # 'Donation': '1', # 捐贈註記
        # 'LoveCode': '168001', # 捐贈碼
        # 'Print': '1',
        # 'InvoiceItemName': '測試商品1|測試商品2',
        # 'InvoiceItemCount': '2|3',
        # 'InvoiceItemWord': '個|包',
        # 'InvoiceItemPrice': '35|10',
        # 'InvoiceItemTaxType': '1|1',
        # 'InvoiceRemark': '測試商品1的說明|測試商品2的說明',
        # 'DelayDay': '0', # 延遲天數
        # 'InvType': '07', # 字軌類別
    }

    # 建立實體
    ecpay_payment_sdk = module.ECPayPaymentSdk(
        MerchantID='2000214',
        HashKey='5294y06JbISpM5x9',
        HashIV='v77hoKGq4kWxNNIS'
    )

    # 合併延伸參數
    order_params.update(extend_params_1)
    order_params.update(extend_params_2)

    # 合併發票參數
    order_params.update(inv_params)

    try:
        # 產生綠界訂單所需參數
        final_order_params = ecpay_payment_sdk.create_order(order_params)

        # 產生 html 的 form 格式
        action_url = 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5'  # 測試環境
        # action_url = 'https://payment.ecpay.com.tw/Cashier/AioCheckOut/V5' # 正式環境
        html = ecpay_payment_sdk.gen_html_post_form(action_url, final_order_params)
        # print("html: ", html)
    except Exception as error:
        print('An exception happened: ' + str(error))
        return False
    return html


def ECPAY_TradeInfo(MerchantTradeNo):
    spec = importlib.util.spec_from_file_location(
    "ecpay_payment_sdk",
    "./sdk/ecpay_payment_sdk.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    MerchantTradeNo = MerchantTradeNo
    order_search_params = {
        'MerchantTradeNo': MerchantTradeNo,
        'TimeStamp': int(time.time())
    }

    # 建立實體
    ecpay_payment_sdk = module.ECPayPaymentSdk(
        MerchantID='2000214',
        HashKey='5294y06JbISpM5x9',
        HashIV='v77hoKGq4kWxNNIS'
    )

    try:
        # 介接路徑
        query_url = 'https://payment-stage.ecpay.com.tw/Cashier/QueryTradeInfo/V5'  # 測試環境
        # query_url = 'https://payment.ecpay.com.tw/Cashier/QueryTradeInfo/V5' # 正式環境

        # 查詢訂單
        query_result = ecpay_payment_sdk.order_search(
            action_url=query_url,
            client_parameters=order_search_params)
        # pprint.pprint(query_result)

    except Exception as error:
        print('An exception happened: ' + str(error))
    return query_result

@transaction.atomic
def Update_Vacancy(schedule_id, learner_count):
    # Update vacancy and available status(only check vacancy)
    schedule_id = schedule_id
    learner_count = learner_count
    try:
        with transaction.atomic():
            schedule = ClassSchedules.objects.select_for_update().get(pk= schedule_id)
    except ObjectDoesNotExist:
        return False
    vacancy = schedule.vacancy
    if (vacancy - learner_count) <0:
        return False
    elif (vacancy - learner_count) == 0:
        schedule.vacancy = vacancy - learner_count
        schedule.available_status = 3
        schedule.save()
        return True
    else:
        print ('before -:', schedule.vacancy)
        schedule.vacancy = vacancy - learner_count
        print ('after -:', schedule.vacancy)
        schedule.save()
        return True

def GetNewTransNo(last_trans_no):
    if not last_trans_no:
        today_y = int(str(date.today().year)[2:4])
        today_m = date.today().month
        new_y = today_y
        new_m = today_m
        new_m = str(new_m).zfill(2)
        new_n = 1
        new_n = str(new_n).zfill(6)
        new_no = str(new_y) + new_m + new_n
        return new_no
    last_trans_y = int(last_trans_no[0:2])
    last_trans_m = int(last_trans_no[2:4])
    last_trans_n = int(last_trans_no[4:11])
    today_y = int(str(date.today().year)[2:4])
    today_m = date.today().month
    if last_trans_y == today_y:
        new_y = today_y
        if last_trans_m == today_m:
            new_m = today_m
            new_n = last_trans_n + 1
        elif last_trans_m != today_m:
            new_m = today_m
            new_n = 1
    elif last_trans_y != today_y:
        new_y = today_y
        new_m = today_m
        new_n = 1
    new_m = str(new_m).zfill(2)
    new_n = str(new_n).zfill(6)
    new_no = str(new_y) + new_m + new_n
    return new_no

def GetNewTransItemNo(last_trans_no):
    last_trans_y = int(last_trans_no[0:2])
    last_trans_m = int(last_trans_no[2:4])
    last_trans_d = int(last_trans_no[4:6])
    print ('last_trans_d', last_trans_d)
    last_trans_n = int(last_trans_no[6:10])
    today_y = int(str(date.today().year)[2:4])
    today_m = date.today().month
    today_d = date.today().day
    print ('last_trans_n', last_trans_n)
    print ('today_d', today_d)
    if last_trans_y == today_y:
        new_y = today_y
        if last_trans_m == today_m:
            new_m = today_m
            if last_trans_d == today_d:
                new_d = today_d
                new_n = last_trans_n + 1
            elif last_trans_d != today_d:
                new_d = today_d
                new_n = 1
        elif last_trans_m != today_m:
            new_m = today_m
            new_d = today_d
            new_n = 1
    elif last_trans_y != today_y:
        new_y = today_y
        new_m = today_m
        new_d = today_d
        new_n = 1
    new_m = str(new_m).zfill(2)
    new_d = str(new_d).zfill(2)
    new_n = str(new_n).zfill(3)
    new_no = str(new_y) + new_m + new_d + new_n
    print ('new_no', new_no)
    return new_no


@transaction.atomic
def Update_Transaction(temp_id, schedule_id, learners, class_info, credict_return_data=[]):
    # credict_return_data = {'ATMAccBank': '', 'ATMAccNo': '',  'AlipayID': '', 'AlipayTradeNo': '', 'CustomField1': {'schedule_id': 'zpeexbynq0lazeymm4rs'}, 'CustomField2':{'guest_id': 'feb81dd2-8824-41d3-81b6-31f0b8a16e8c'}, 'CustomField3': '', 'CustomField4': '', 'ExecTimes': '', \
    #     'Frequency': '', 'HandlingCharge': '55', 'ItemName': [{'profile_name': 'Candy Yo', 'profile_dob': '2016/3/28', 'profile_note': ''}, {'profile_name': 'Andrew Yo', \
    #     'profile_dob': '2016/5/28', 'profile_note': 'cc'}],'MerchantID': '2000214', 'MerchantTradeNo': 'NO20190508043305', 'PayFrom': '', 'PaymentDate': '2019/05/08 12:33:27', \
    #     'PaymentNo': '', 'PaymentType': 'Credit_CreditCard', 'PaymentTypeChargeFee': '55', 'PeriodAmount': '', 'PeriodType': '', 'StoreID': '',  'TenpayTradeNo': '', \
    #     'TotalSuccessAmount': '', 'TotalSuccessTimes': '', 'TradeAmt': '2000', 'TradeDate': '2019/05/08 12:33:05', 'TradeNo': '1905081233057184', 'TradeStatus': '1', 'WebATMAccBank': '', \
    #     'WebATMAccNo': '', 'WebATMBankName': '', 'amount': '2000', 'auth_code': '777777',  'card4no': '2222', 'card6no': '431195', \
    #     'eci': '0', 'gwsr': '10853033', 'process_date': '2019/05/08 12:33:27', 'red_dan': '0', 'red_de_amt': '0', 'red_ok_amt': '0', 'red_yet': '0', \
    #     'staed': '0', 'stage': '0', 'stast': '0'}
    # schedule_id = credict_return_data['CustomField1']['schedule_id']
    # learners = credict_return_data['ItemName']
    # # print ('learners', learners)
    # class_info = GetClassInfo(schedule_id)
    # learners_count = len(learners)
    credict_return_data = credict_return_data

    schedule_id = schedule_id
    learners = learners
    class_info = class_info
    learners_count = len(learners)
    temp_info = GetGuestTempInfo(temp_id)

    try:
        schedule = ClassSchedules.objects.get(pk= schedule_id)
    except ObjectDoesNotExist:
        return '006'
    option = schedule.option
    branch = option.branch
    classes = branch.classes
    vendor = classes.vendor
    country_list = CountryLists.objects.get(country_name = vendor.vendor_country)
    # Sub toal without using any coupon for ecredit
    sub_total = learners_count * class_info['option_price']

    # Update transaction
    new_transaction = Transaction()
    data = {}
    last_trans = Transaction.objects.latest('transaction_no')
    print ('latest transactions, ', last_trans)
    last_trans_no = last_trans.transaction_no
    new_transaction_number = GetNewTransNo(last_trans_no)
    data['transaction_no'] = new_transaction_number
    data['ecredits_price'] = 0
    data['guest_id'] = temp_info.guest_id
    data['price_prefix'] = class_info['price_prefix']
    data['total_price'] = sub_total
    data['class_count'] = 1
    # To add device_type from platform or not, it's a question
    # device_type = {0:'Guest', 1:'iOS', 2:'Android', 3:'iOS', 4:'Web', 5:'edPOS'}
    data['device_type'] = 0

    # stripe_charge_id = models.CharField(max_length=255, blank=True, null=True)
    if credict_return_data == 'NEWEBPAY':
        data['newebpay_merchant_trade_no'] = temp_id
    elif type(credict_return_data) is dict :
        data['ecpay_merchant_trade_no'] = credict_return_data['MerchantTradeNo']
    
    # print ('data', data)
    for key,value in data.items():
        setattr(new_transaction, key, value)
    new_transaction.save()
    # print ('uuid', str(uuid.uuid4()))

    # Update_Transaction_item
    new_transaction_item = TransactionItems()
    item_data = {}
    # Update transaction no in item
    vendorCountryCode = country_list.country_code_alpha3
    vendor_code = vendor.vendor_code
    branchCode = VendorBranches.objects.get(pk = branch.branch_id).branch_code
    code_prefix = vendorCountryCode + vendor_code + branchCode
    last_trans_item = TransactionItems.objects.filter(booking_no__contains=code_prefix).order_by('-booking_no')
    
    if last_trans_item:
        last_trans_item = last_trans_item[0]
        # print ('last_trans_item', last_trans_item.booking_no)
        last_trans_item_no = last_trans_item.booking_no.replace(code_prefix, '')
        new_trans_item_no = GetNewTransItemNo(last_trans_item_no)
        item_data['booking_no'] = code_prefix + new_trans_item_no
    else:
        last_trans_item_no = '000000000'
        new_trans_item_no = GetNewTransItemNo(last_trans_item_no)
        item_data['booking_no'] = code_prefix + new_trans_item_no
    item_data['transaction_id'] = new_transaction.pk
    item_data['booking_class_id'] = class_info['class_id']
    item_data['booking_schedule_id'] = schedule_id
    item_data['vendor_id'] = class_info['vendor_id']
    item_data['vendor_branch_id'] = class_info['branch_id']
    item_data['class_name'] = class_info['class_name']
    item_data['option_name'] = class_info['option_name']
    item_data['schedule_name'] = class_info['schedule_name']
    item_data['vendor_name'] = class_info['vendor_name']
    # item_data['school_coupon_id'] = 'NULL'
    # item_data['school_coupon_code'] = 'NULL'
    item_data['original_price'] = sub_total
    item_data['register_price'] = 0
    item_data['school_coupon_price'] = 0
    item_data['merchandise_price'] = 0
    item_data['total_price'] = sub_total
    # item_data['special_note'] = ''
    item_data['branch_address'] = class_info['address']
    item_data['branch_name'] = class_info['branch_name']
    item_data['age_min'] = classes.age_min
    item_data['age_max'] = classes.age_max
    item_data['learner_count'] = learners_count
    item_data['class_date'] = class_info['schedule_name']
    item_data['class_time'] = schedule.start_time + '-' + schedule.end_time
    item_data['redeem'] = 0
    item_data['confirm'] = 0
    item_data['price_prefix'] = class_info['price_prefix']
    # item_data['special_name'] = ''
    # item_data['special_discount'] = ''
    for key,value in item_data.items():
        setattr(new_transaction_item, key, value)
    new_transaction_item.save()

    # Update booking_class
    new_booking_class = BookingClasses()
    book_data = {}
    book_data['transaction_item_id'] = new_transaction_item.pk
    book_data['class_name'] = class_info['class_name']
    book_data['vendor_id'] = class_info['vendor_id']
    book_data['description'] = classes.description
    book_data['age_min'] = classes.age_min
    book_data['age_max'] = classes.age_max
    book_data['cover_image'] = classes.cover_image
    # book_data['image_list'] = classes.image_list
    book_data['youtube_code'] = classes.youtube_code
    book_data['teaching_type_1'] = classes.teaching_type_1
    book_data['teaching_type_2'] = classes.teaching_type_2
    book_data['teaching_type_3'] = classes.teaching_type_3
    book_data['teaching_type_4'] = classes.teaching_type_4
    book_data['teaching_type_5'] = classes.teaching_type_5
    book_data['teaching_type_6'] = classes.teaching_type_6
    book_data['teaching_type_7'] = classes.teaching_type_7
    book_data['teaching_type_8'] = classes.teaching_type_8
    book_data['comment_status'] = classes.comment_status
    book_data['view_count'] = classes.view_count
    book_data['ad_paid'] = classes.ad_paid
    book_data['start_date'] = schedule.start_date
    book_data['end_date'] = schedule.end_date
    for key,value in book_data.items():
        setattr(new_booking_class, key, value)
    new_booking_class.save()

    # Update branch history
    new_branch_history = BranchHistories()
    hist_data = {}
    hist_data['booking_class_id'] = new_booking_class.pk
    hist_data['class_branch'] = branch.class_branch
    hist_data['class_id'] = branch.classes.pk
    hist_data['country'] = branch.country
    hist_data['city'] = branch.city
    hist_data['address'] = branch.address
    hist_data['latitude'] = branch.latitude
    hist_data['longitude'] = branch.longitude
    for key,value in hist_data.items():
        setattr(new_branch_history, key, value)
    new_branch_history.save()

    temp_learners = deepcopy(learners)
    # print ('WTDDDDDDDDDDDDDDD', temp_learners)
    
    # Update transactionItemProfile
    for learner in temp_learners:
        prof_data = {}
        new_transactionitem_profile = TransactionItemProfiles.objects.create(id =str(uuid.uuid4())[0:30], profile_dob = timezone.now())
        # print ('new_transactionitem_profile', new_transactionitem_profile)
        prof_data['transaction_item_id'] = new_transaction_item.pk
        prof_data['profile_id'] = learner['profile_id'] if learner.get('profile_id', None) else ''
        prof_data['profile_name'] = learner['profile_name'] if learner.get('profile_name', None) else ''
        # print ('learner[profile_dob]', learner['profile_dob'])
        if learner.get('profile_dob', None):
            try:
                with transaction.atomic():
                    learner['profile_dob'] = datetime.strptime(learner['profile_dob'], '%Y/%m/%d').date()
                    print ('change format 1')
            except ValueError:
                learner['profile_dob'] = datetime.strptime(learner['profile_dob'], '%Y-%m-%d').date()
                print ('change format 2')
            except:
                prof_data['profile_dob'] = learner['profile_dob']
                print ('change format 3')
                return '013'
        # print ('learner[profile_dob] after', learner['profile_dob'])
        prof_data['profile_dob'] = learner['profile_dob']
        # print ('end of learner dob')
        prof_data['profile_note'] = learner['profile_note'] if learner.get('profile_note', None) else ''
        print ('end of learner note')
        for key,value in prof_data.items():
            print ('key, value', key, ',', value)
            setattr(new_transactionitem_profile, key, value)
        new_transactionitem_profile.save()
    
    # Get temporary guest info, send mail, then delete
    temp_guest = GuestTemporaryInfo.objects.get(id = temp_id)
    

    # Send email to both customer and partner if Transaction done
    mail_data = {
        "guest_email": temp_info.email,
        "partner_email": vendor.vendor_email,
        "class_hold_by": class_info['vendor_name'],
        "branch": class_info['branch_name'],
        "learners": learners,
        "class_name": class_info['class_name'],
        "class_option": class_info['option_name'],
        "class_date" : class_info['schedule_name'],
        "class_time" : schedule.start_time + '-' + schedule.end_time,
        "price": str(sub_total),
        "payment_type": 'Credit',
        "customer_name": temp_guest.last_name + temp_guest.first_name,
        "customer_mobile": temp_guest.mobile,
        "transaction_number": new_transaction_number
    }
    # print ('mail_data', mail_data)
    customer_service = public_url_sendmail+'/sendmail/guest/'
    partner_service = public_url_sendmail+'/sendmail/partner/'
    customer_mail_send = requests.post(customer_service,json=mail_data)
    print ('customer_mail_send', customer_mail_send)
    partner_mail_send = requests.post(partner_service,json=mail_data)
    if customer_mail_send.status_code != 200 or partner_mail_send.status_code != 200:
        print ('customer_mail_send.status_code', customer_mail_send.status_code)
        return '020'
    customer_mail_send = eval(customer_mail_send.content)
    partner_mail_send = eval(partner_mail_send.content)
    if not customer_mail_send['code'] == '005000':
        return customer_mail_send
    elif not partner_mail_send['code'] == '005000':
        return partner_mail_send
    else:
        temp_guest.delete()
        return '014'

@transaction.atomic
def Update_Free_Transaction(temp_id, guest_id, schedule_id, learners):
    # Get payment informations
    # credict_return_data = {'CustomField2':str({'g_id':guest_id}), 'CustomField3':str({'t_id':temp_id}), 'MerchantTradeNo':''}
    # Get all needed class info by schedule_id
    class_info = GetClassInfo(schedule_id)

    # Lock vacancy and update
    learner_count = len(learners)
    lock = Update_Vacancy(schedule_id, learner_count)
    if not lock:
        return APIHandler.catch('Vacancy not enough or schedule error', code='012')
    
    # Start transaction to transactions
    trans = Update_Transaction(temp_id, schedule_id, learners, class_info)
    if trans == '006':
        return '006'
    elif trans == '013':
        return '013'
    elif trans == '014':
        return '014'
    elif trans == '020':
        return '020'
    else:
        return '017'

@transaction.atomic
def Update_Counter_Transaction(temp_id):
    # Get temp info and store like transaction item
    temp_info = GetGuestTempInfo(temp_id)
    if not temp_info:
        return '004'
    schedule_id = temp_info.schedule_id
    temp_learners = eval(deepcopy(temp_info.learners))
    # print ('temp_learners', temp_learners)
    learners = eval(temp_info.learners)
    class_info = GetClassInfo(schedule_id)
    learners_count = len(learners)
    
    try:
        schedule = ClassSchedules.objects.get(pk= schedule_id)
    except ObjectDoesNotExist:
        return '006'
    option = schedule.option
    branch = option.branch
    classes = branch.classes
    vendor = classes.vendor
    sub_total = learners_count * class_info['option_price']

    # Update transaction
    counter_transaction = TransactionCounterPay()
    data = {}

    last_trans = TransactionCounterPay.objects.latest('counter_transaction_no')
    print ('latest transactions, ', last_trans)
    last_trans_no = last_trans.counter_transaction_no
    print ('GetNewTransNo(last_trans_no)', GetNewTransNo(last_trans_no))
    new_transaction_number = GetNewTransNo(last_trans_no)
    data['counter_transaction_no'] = new_transaction_number
    data['guest_id'] = temp_info.guest_id
    data['price_prefix'] = class_info['price_prefix']
    data['total_price'] = sub_total
    # To add device_type from platform or not, it's a question
    # device_type = {0:'Guest', 1:'iOS', 2:'Android', 3:'iOS', 4:'Web', 5:'edPOS', 6:'Counter'}
    data['device_type'] = 6
    data['booking_class_id'] = class_info['class_id']
    data['booking_schedule_id'] = schedule_id
    data['vendor_id'] = class_info['vendor_id']
    data['vendor_branch_id'] = class_info['branch_id']
    data['class_name'] = class_info['class_name']
    data['option_name'] = class_info['option_name']
    data['schedule_name'] = class_info['schedule_name']
    data['vendor_name'] = class_info['vendor_name']
    data['branch_name'] = class_info['branch_name']
    data['learner_count'] = learners_count
    data['class_date'] = class_info['schedule_name']
    data['class_time'] = schedule.start_time + '-' + schedule.end_time
    data['country'] = branch.country
    data['city'] = branch.city
    data['learners'] = learners


    for key,value in data.items():
        setattr(counter_transaction, key, value)
    counter_transaction.save()
    
    # Get temporary guest info, send mail, then delete
    temp_guest = GuestTemporaryInfo.objects.get(id = temp_id)
    
    # Send email if Transaction done
    # Send email to both customer and partner if Transaction done
    mail_data = {
        "guest_email": temp_info.email,
        "partner_email": vendor.vendor_email,
        "class_hold_by": class_info['vendor_name'],
        "branch": class_info['branch_name'],
        "learners": temp_learners,
        "class_name": class_info['class_name'],
        "class_option": class_info['option_name'],
        "class_date" : class_info['schedule_name'],
        "class_time" : schedule.start_time + '-' + schedule.end_time,
        "price": str(sub_total),
        "payment_type": 'Cash',
        "customer_name": temp_guest.last_name + temp_guest.first_name,
        "customer_mobile": temp_guest.mobile,
        "transaction_number": new_transaction_number
    }
    print ('mail data', mail_data)
    customer_service = public_url_sendmail+'/sendmail/guest/'
    partner_service = public_url_sendmail+'/sendmail/partner/'
    customer_mail_send = requests.post(customer_service,json=mail_data)
    partner_mail_send = requests.post(partner_service,json=mail_data)
    # print ('customer_mail_send', customer_mail_send)
    if customer_mail_send.status_code != 200 or partner_mail_send.status_code != 200:
        return '020'
    customer_mail_send = eval(customer_mail_send.content)
    partner_mail_send = eval(partner_mail_send.content)
    # print ('customer_mail_send2', customer_mail_send)
    if not customer_mail_send['code'] == '005000':
        return customer_mail_send
    elif not partner_mail_send['code'] == '005000':
        return partner_mail_send
    else:
        temp_guest.delete()
        return '016'

def GetHistroyLearners(email):
    # Use email to filter history
    guest_infos = GuestInfos.objects.filter(email = email)
    transactions = Transaction.objects.filter(guest_id__in = [guest.id for guest in guest_infos])
    transaction_items = TransactionItems.objects.filter(transaction_id__in = [transaction.id for transaction in transactions])
    transaction_item_profile = TransactionItemProfiles.objects.filter(transaction_item_id__in = [transaction_item.id for transaction_item in transaction_items])
    #  Use name to further filter history
    if transaction_item_profile:
        name_set = set()
        for profile in transaction_item_profile:
            name_set.add(profile.profile_name)
        # print(name_set)
        item_list = []
        for name in name_set:
            item_list.append(TransactionItemProfiles.objects.filter(profile_name = name).order_by('-date_added')[0])
        # print('item_list[0]', item_list[0])

        # for item in item_list:
        serialized_item = TransactionItemProfilesSerializer(item_list, many=True).data
        # serialized_item = json.dumps(serialized_item)
        return serialized_item
    else :
        return ('No learner info')

        # name_list = transaction_item_profile.objects.values_list('email', flat=True).distinct()