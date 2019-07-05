import os
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from helper.helper import APIHandler
from .services import *
# Create your views here.

class Activate_Topex_Customer(APIView):
    def get(self, request):
        id_list = GET_ALL_TOPEX_MEMBER()
        return APIHandler.catch(data={"topex_id_list":id_list}, code='BA1')

    def post(self, request):
        customer_id = request.data.get('customer_id')
        update_status = ACTIVATE_TOPEX_CUSTOMER(customer_id)
        return APIHandler.catch(data={"topex_id":update_status}, code='BA0')

    def delete(self, request):
        customer_id = request.data.get('customer_id')
        update_status = REMOVE_TOPEX_CUSTOMER(customer_id)
        return APIHandler.catch(data={"topex_id":update_status}, code='BA2')

