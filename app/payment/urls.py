from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    # path('hello_world/', views.Hello.as_view()),
    path('guest_tempinfo/', views.StoreGuestTempInfo.as_view()),
    path('newebpay_guest_paynow/', views.GuestPaynow.as_view()),
    path('ecpay_return_data/', views.ECPAY_ReturnData.as_view()),
    path('newebpay_return_data/', views.NEWEBPAY_ReturnData.as_view()),
    path('pay_by_counter/', views.PayByCounter.as_view()),
    path('pay_by_mail/', views.PayByMail.as_view()),
    url(r'^url_guest_pay/(?P<temp_id>[\w\x2D]+)/$', views.MailGuestPaynow.as_view()),
    path('close_page/', views.ClosePage.as_view()),
    # path('show_result/', views.Result.as_view()),
    path('history_learners/', views.HistoryLearners.as_view()),
]