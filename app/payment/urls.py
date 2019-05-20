from django.urls import path, re_path
from . import views

urlpatterns = [
    # path('hello_world/', views.Hello.as_view()),
    path('guesttempinfo/', views.StoreGuestTempInfo.as_view()),
    path('guestpaynow/', views.GuestPaynow.as_view()),
    path('return_data/', views.ECPAY_ReturnData.as_view()),
    path('free/', views.ECPAY_ReturnData_Free.as_view()),
    # path('test/', views.TEST.as_view()),
    path('show_result/', views.Result.as_view()),
    path('history_learners/', views.HistoryLearners.as_view()),
]