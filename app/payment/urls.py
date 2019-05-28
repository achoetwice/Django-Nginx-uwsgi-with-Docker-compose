from django.urls import path, re_path
from . import views

urlpatterns = [
    # path('hello_world/', views.Hello.as_view()),
    path('guest_tempinfo/', views.StoreGuestTempInfo.as_view()),
    path('newebpay_guest_paynow/', views.GuestPaynow.as_view()),
    path('ecpay_return_data/', views.ECPAY_ReturnData.as_view()),
    path('newebpay_return_data/', views.NEWEBPAY_ReturnData.as_view()),
    path('free/', views.ECPAY_ReturnData_Free.as_view()),
    path('pay_by_counter/', views.PayByCounter.as_view()),
    path('close_page/', views.ClosePage.as_view()),
    # path('show_result/', views.Result.as_view()),
    path('history_learners/', views.HistoryLearners.as_view()),
]