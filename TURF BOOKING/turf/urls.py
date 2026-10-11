from django.urls import path
from . import views

urlpatterns = [

    # ─── Public / General Pages ─────────────────────────────────────────────
    path('', views.index, name="index"),
    path('index', views.index, name="index"),
    path('about', views.about, name="about"),
    path('contact', views.contact, name="contact"),
    path('contactus', views.contactus, name="contactus"),
    path('services', views.services, name="services"),
    path('feedback/<int:fid>', views.feedbacks, name="feedback"),
    path('addfeedback', views.addfeedback, name='addfeedback'),

    # ─── Authentication ──────────────────────────────────────────────────────
    path('login', views.loginpage, name="login"),
    path('loginuser', views.loginuser, name="loginuser"),
    path('register', views.register, name="register"),
    path('createuser', views.createuser, name="createuser"),
    path('logout', views.logout, name="logout"),
    path('forgotpasswordpage', views.forgotpasswordpage, name="forgotpasswordpage"),
    path('forgotpassword', views.forgotpassword, name="forgotpassword"),
    path('verifyotppage', views.verifyotppage, name="verifyotppage"),
    path('verifyotp', views.verifyotp, name="verifyotp"),
    path('resetpasswordpage', views.resetpasswordpage, name="resetpasswordpage"),
    path('resetpassword', views.resetpassword, name="resetpassword"),
    path('resendotp', views.resendotp, name="resendotp"),
    path('changepwdpage', views.changepwdpage, name="changepwdpage"),
    path('changepwd', views.changepwd, name="changepwd"),

    # ─── User Profile ────────────────────────────────────────────────────────
    path('userprofile', views.userprofile, name="userprofile"),
    path('edituserprofile', views.edituserprofile, name="edituserprofile"),
    path('updateprofile', views.updateprofile, name="updateprofile"),
    path('completeprofilepage', views.completeprofilepage, name="completeprofilepage"),
    path('completeprofile', views.completeprofile, name="completeprofile"),

    # ─── Turf — User Side ───────────────────────────────────────────────────
    path('userturflist', views.userturflist, name="userturflist"),
    path('turfdetails/<int:id>', views.turfdetails, name="turfdetails"),
    path('booking', views.userbooking, name="booking"),
    path('selectdate/<int:id>', views.selectdate, name="selectdate"),
    path('selectslotpage', views.selectslotpage, name="selectslotpage"),
    path('selectslot', views.selectslot, name="selectslot"),
    path('userbookings', views.userbookings, name="userbookings"),
    path('userpayemnts', views.userpayemnts, name="userpayemnts"),

    # ─── Payment — Razorpay ──────────────────────────────────────────────
    path('initiate_payment', views.initiate_payment, name="initiate_payment"),
    path('verify_payment',   views.verify_payment,   name="verify_payment"),
    path('payment_success',  views.payment_success,  name="payment_success"),

    # ─── Turf — Manager Side ────────────────────────────────────────────────
    path('addturfpage', views.addturfpage, name="addturfpage"),
    path('addturf', views.addturf, name="addturf"),
    path('turflist', views.turflist, name="turflist"),
    path('editturf/<int:id>', views.editturfpage, name="editturf"),
    path('updateturf/<int:id>', views.updateturf, name="updateturf"),
    path('removeturf/<int:id>', views.removeturf, name="removeturf"),
    path('timeslots', views.timeslots, name="timeslots"),
    path('saveslot', views.saveslot, name="saveslot"),
    path('viewslots', views.viewslots, name="viewslots"),
    path('removeslot/<int:id>', views.removeslot, name="removeslot"),
    path('turfbookings', views.turfbookings, name="turfbookings"),
    path('turfpayments', views.turfpayments, name="turfpayments"),
    path('fetchturfs', views.fetchturfs, name="fetchturfs"),

]
