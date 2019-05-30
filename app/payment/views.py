import os
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
import requests
import json

from payment.serializers import *
from helper.helper import APIHandler

from .models import CurrencyLists, AwardCouponHistories
from .services import *

# class Apilist(APIView):
#     def get(self, request):
#         return render(request, 'rest_framework/api.html')

public_url = os.getenv('public_url')

class StoreGuestTempInfo(APIView):
    def post(self, request):

        # Get datas and store
        email = request.data.get('customer_email')
        first_name = request.data.get('customer_firstname')
        last_name = request.data.get('customer_lastname')
        customer_mobile = request.data.get('customer_mobile')
        learners = request.data.get('learners')
        schedule_id = request.data.get('schedule_id')
        auto_create_account = request.data.get('auto_create_account', 0)
        print ('temp guest info, ', type(learners))
        if not email or not first_name or not last_name or not customer_mobile or not auto_create_account:
            return APIHandler.catch('lack of informations', code='001')
        

        # Insert Guest information
        guest_id = SaveGuestInfos(email, first_name, last_name, customer_mobile)
        print ('guest_id', guest_id)
        if not guest_id:
            return APIHandler.catch('Saving guest info failed', code='009')
        
        temp_id = StoreTempInfo(email, first_name, last_name, customer_mobile, learners, schedule_id, auto_create_account, guest_id)

        return APIHandler.catch(data={"temp_id":temp_id}, code='002')
        # Return store id

class GuestPaynow(APIView):
    def post(self, request):
        # Get datas and check exist
        temp_id = request.data.get('temp_id')
        if not temp_id:
            return APIHandler.catch('Please provide temp_id', code='003')
        temp_info = GetGuestTempInfo(temp_id)
        if not temp_info:
            return APIHandler.catch('Missing temp info', code='004')
        email = temp_info.email
        first_name = temp_info.first_name
        last_name = temp_info.last_name
        customer_mobile = temp_info.mobile
        learners = eval(temp_info.learners)
        schedule_id = temp_info.schedule_id
        # ECPAY_token = request.data.get('ECPAY_token')
        # coupon = request.data.get('coupon')
        auto_create_account = temp_info.auto_create_account
        if not email or not first_name or not last_name or not customer_mobile:
            return APIHandler.catch('Temp info not complete', code='005')

        # Get all needed class info by schedule_id
        class_info = GetClassInfo(schedule_id)
        if not class_info:
            return APIHandler.catch('Schedule not exist', code='006')
        # Confirm that learners and vacancy
        learner_count = len(learners)
        if not learners:
            return APIHandler.catch('Missing learner info', code='007')
        elif learner_count > class_info['vacancy']:
            return APIHandler.catch('No vacancy', code='008')

        # # # Confirm age is valid

        guest_id = temp_info.guest_id
        
        # Handle the free class by skip ECPAY
        if class_info['option_price'] <= 0:
            trans = Upate_Free_Transaction(temp_id, guest_id, schedule_id, learners)
            if trans == '006':
                return APIHandler.catch('Schedule not exist', code='006')
            elif trans == '013':
                return APIHandler.catch('Learner dob format not legible', code='013')
            elif trans == '014':
                print ('trans', trans)
                return APIHandler.catch('Success, free class, go to transactions', code='010')
            else:
                return APIHandler.catch('Free transaction problem', code='017')

        # Start to ECpay and redirect to payment html 
        # html = ECPAY(schedule_id, learners, guest_id, temp_id)
        pay_data = NEWEBPAY(schedule_id, learners, guest_id, temp_id)
        # print (html)
        # if html:
        #     return render(request, 'ECPAY_pay.html', {'html':html})
        if pay_data:
            return render(request, 'NEWEBPAY_pay.html', {'data':pay_data})
        else:
            return APIHandler.catch('Fail to generate payment page', code='011')

class NEWEBPAY_ReturnData(APIView):
    def post(self, request):
        # Get transaction data
        data = request.data
        print ('newebpay_data', data)
        data = NEWEBPAY_Decrypt(data['TradeInfo'])
        print ('data', data)
        temp_id = data['Result']['MerchantOrderNo']
        temp_info = GetGuestTempInfo(temp_id)
        schedule_id = temp_info.schedule_id
        if not temp_info:
            return APIHandler.catch('Missing temp info', code='004')
        learners = eval(temp_info.learners)
        print ('learnerssss', learners)
        # Get all needed class info by schedule_id
        class_info = GetClassInfo(schedule_id)

        # Lock vacancy and update
        learner_count = len(learners)
        lock = Update_Vacancy(schedule_id, learner_count)
        if not lock:
            return APIHandler.catch('Vacancy not enough or schedule error', code='012')

        # Get credict_return_data
        credict_return_data = 'NEWEBPAY'
        # Todo here: check credict card record in newebpay
        
        # Start transaction to transactions
        trans = Upate_Transaction(temp_id, schedule_id, learners, class_info, credict_return_data)
        if trans == '006':
            return APIHandler.catch('Schedule not exist', code='006')
        elif trans == '013':
            return APIHandler.catch('Learner dob format not legible', code='013')
        else:
            print ('trans', trans)
            return APIHandler.catch('ok', code='014')

class ECPAY_ReturnData(APIView):
    def post(self, request):
        data = request.data
        MerchantTradeNo = data['MerchantTradeNo']
        trade = ECPAY_TradeInfo(MerchantTradeNo)

        # Get payment informations
        credict_return_data = trade
        schedule_id = eval(data['CustomField1'])['s_id']
        temp_id = eval(data['CustomField3'])['t_id']
        temp_info = GetGuestTempInfo(temp_id)
        if not temp_info:
            return APIHandler.catch('Missing temp info', code='004')
        learners = eval(temp_info.learners)
        print ('learnerssss', learners)
        # Get all needed class info by schedule_id
        class_info = GetClassInfo(schedule_id)

        # Lock vacancy and update
        learner_count = len(learners)
        lock = Update_Vacancy(schedule_id, learner_count)
        if not lock:
            return APIHandler.catch('Vacancy not enough or schedule error', code='012')
        
        # Start transaction to transactions
        trans = Upate_Transaction(temp_id, schedule_id, learners, class_info, credict_return_data)
        if trans == '006':
            return APIHandler.catch('Schedule not exist', code='006')
        elif trans == '013':
            return APIHandler.catch('Learner dob format not legible', code='013')
        else:
            print ('trans', trans)
            return APIHandler.catch('ok', code='014')

# class ECPAY_ReturnData_Free(APIView):
#     def post(self, request):
#         data = request.data

#         # Get payment informations
#         temp_id = request.data.get('temp_id')
#         credict_return_data = {'CustomField2':str({'g_id':data['guest_id']}), 'CustomField3':str({'t_id':data['temp_id']}), 'MerchantTradeNo':''}
#         schedule_id = data['schedule_id']
#         learners = data['learners']
#         # Get all needed class info by schedule_id
#         class_info = GetClassInfo(schedule_id)
#         print ('class_info', class_info)

#         # Lock vacancy and update
#         learner_count = len(learners)
#         lock = Update_Vacancy(schedule_id, learner_count)
#         if not lock:
#             return APIHandler.catch('Vacancy not enough or schedule error', code='012')
        
#         # Start transaction to transactions
#         trans = Upate_Transaction(temp_id, schedule_id, learners, class_info, credict_return_data)
#         if trans == '006':
#             return APIHandler.catch('Schedule not exist', code='006')
#         elif trans == '013':
#             return APIHandler.catch('Learner dob format not legible', code='013')
#         else:
#             print ('trans', trans)
#             return APIHandler.catch(data, code='014')

class PayByCounter(APIView):
    def post(self, request):
        temp_id = request.data.get('temp_id')
        counter_rsult = Update_CounterTransaction
        return APIHandler.catch('Counter transaction saved', code='016')

class ClosePage(APIView):
    def get(self, request):
        return render(request, 'close_page.html')

class HistoryLearners(APIView):
    def get(self, request):
        # Use get method with parameters?=
        email = request.GET.get('guest_email')
        # print ('email:', email)
        learners = GetHistroyLearners(email)

        return APIHandler.catch(data=learners, code='015')

# class TEST(APIView):
#     def get(self, request):
#         schedule_id = 'C'
#         learners = [{'profile_name': 'Candy Yo', 'profile_dob': '2016/3/28', 'profile_note': ''}, {'profile_name': 'Candys Yo', 'profile_dob': '2016/3/28', 'profile_note': 'cc'}]
#         guest_id = 'CC'
#         html = ECPAY(schedule_id, learners, guest_id)
#         class_info = 'I'
#         credict_return_data = 'R'
#         Upate_Transaction(credict_return_data, schedule_id, learners, class_info)
#         from django.utils import timezone
#         # print (timezone.now())

#         return render(request, 'ECPAY_pay.html', {'html':html})



