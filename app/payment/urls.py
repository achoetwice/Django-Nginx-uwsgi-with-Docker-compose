from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    # path('hello_world/', views.Hello.as_view()),
    path('guest_tempinfo/', views.StoreGuestTempInfo.as_view()),
    path('newebpay_guest_paynow/', views.GuestPaynow.as_view()),
    path('lej2_customer_paynow/', views.LEJ2_CustomerPaynow.as_view()),
    path('ecpay_return_data/', views.ECPAY_ReturnData.as_view()),
    path('newebpay_return_data/', views.NEWEBPAY_ReturnData.as_view()),
    path('newebpay_return_lej2_data/', views.NEWEBPAY_LEJ2_ReturnData.as_view()),
    path('newebpay_return_premium_data/', views.NEWEBPAY_Premium_ReturnData.as_view()),
    path('pay_by_counter/', views.PayByCounter.as_view()),
    path('pay_by_mail/', views.PayByMail.as_view()),
    url(r'^url_guest_pay/(?P<temp_id>[\w\x2D]+)/$', views.UrlGuestPaynow.as_view()),
    url(r'^lej2_url_customer_pay/(?P<customer_id>[\w\x2D]+)/$', views.LEJ2_Url_CustomerPaynow.as_view()),
    url(r'^premium_url_pay/(?P<service_customer_id>[\w\x2D]+)/$', views.Url_PremiumCustomerPaynow.as_view()),
    path('close_page/', views.ClosePage.as_view()),
    path('show_result/', views.Result.as_view()),
    path('history_learners/', views.HistoryLearners.as_view()),
    path('transaction_no/', views.GetTransactionNo.as_view()),
    path('line_payment_history/', views.LinePaymentHistory.as_view()),
    path('lej2_clean_shoppingcart/', views.LEJ2_CleanUpShoppingCart.as_view()),
    path('lej2_shoppingcart_sumID/', views.LEJ2_GetShoppingcart_Summary_ID.as_view()),
 
]