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
        if not email or not first_name or not last_name or not customer_mobile:
            return APIHandler.success('lack of informations')
        temp_id = StoreTempInfo(email, first_name, last_name, customer_mobile, learners, schedule_id, auto_create_account)
        return APIHandler.success({"temp_id":temp_id})
        # Return store id

class GuestPaynow(APIView):
    def post(self, request):
        # Get datas and check exist
        temp_id = request.data.get('temp_id')
        if not temp_id:
            return APIHandler.success('Missing temp_id')
        temp_info = GetGuestTempInfo(temp_id)
        if not temp_info:
            return APIHandler.success('No temp info')
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
            return APIHandler.success('lack of informations')

        # Get all needed class info by schedule_id
        class_info = GetClassInfo(schedule_id)

        # Confirm that learners and vacancy
        learner_count = len(learners)
        if not learners:
            return APIHandler.success('No learner')
        elif learner_count > class_info['vacancy']:
            return APIHandler.success('No vacancy')

        # # # Confirm age is valid
        # # For edPOS, age_check is done before payment
        # for learner in learners:
        #     Allow = CheckAgeValidation(learner, schedule_id)
        #     if not Allow:
        #         return APIHandler.success('Age not fit')

        # Insert Guest information
        guest_id = SaveGuestInfos(email, first_name, last_name, customer_mobile)
        print ('guest_id', guest_id)
        if not guest_id:
            return APIHandler.success('Guest information not saved')
        
        # TO DO Customer submmission & return customer_id
        
        # Handle the free class by skip ECPAY
        if class_info['option_price'] <= 0:
            url = public_url + '/payment/free/'
            params = {
                'guest_id': guest_id,
                'schedule_id': schedule_id,
                'temp_id': temp_id,
                'learners': learners,
            }
            requests.post(url, json=params)
            return APIHandler.free('Free class, automatically go to Transactions')

        # Start to ECpay and redirect to payment html 
        html = ECPAY(schedule_id, learners, guest_id, temp_id)
        if html:
            return render(request, 'ECPAY_pay.html', {'html':html})
        else:
            return APIHandler.success('success to charge')



class ECPAY_ReturnData(APIView):
    def post(self, request):
        data = request.data
        MerchantTradeNo = data['MerchantTradeNo']
        trade = TradeInfo(MerchantTradeNo)

        # Get payment informations
        credict_return_data = trade
        schedule_id = eval(data['CustomField1'])['s_id']
        temp_id = eval(data['CustomField3'])['t_id']
        learners = GetGuestTempInfo(temp_id)
        # Get all needed class info by schedule_id
        class_info = GetClassInfo(schedule_id)

        # Lock vacancy and update
        learner_count = len(learners)
        lock = Update_Vacancy(schedule_id, learner_count)
        if not lock:
            return APIHandler.success('Vacancy error')
        
        # Start transaction to transactions
        Upate_Transaction(credict_return_data, schedule_id, learners, class_info)

        return Response(data)

class ECPAY_ReturnData_Free(APIView):
    def post(self, request):
        data = request.data

        # Get payment informations
        credict_return_data = {'CustomField2':str({'g_id':data['guest_id']}), 'CustomField3':str({'t_id':data['temp_id']}), 'MerchantTradeNo':''}
        schedule_id = data['schedule_id']
        learners = data['learners']
        # Get all needed class info by schedule_id
        class_info = GetClassInfo(schedule_id)
        print ('class_info', class_info)

        # Lock vacancy and update
        learner_count = len(learners)
        lock = Update_Vacancy(schedule_id, learner_count)
        if not lock:
            return APIHandler.success('Vacancy error')
        
        # Start transaction to transactions
        Upate_Transaction(credict_return_data, schedule_id, learners, class_info)

        return Response(data)

class Result(APIView):
    def post(self, request):
        data = request.data
        return Response(data)

class HistoryLearners(APIView):
    def get(self, request):
        email = request.GET.get('guest_email')
        learners = GetHistroyLearners(email)
        # learners = str(json.dumps(learners))
        return APIHandler.success(data=learners, code='00300N')

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



