import datetime
from datetime import date, datetime
from django.shortcuts import render, redirect
from .models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404


# Create your views here.

def checkuser(request):
    try:
        uid = request.session['login_id']
        userdata = login.objects.get(id=uid)

        try:
            profiledata = user_detail.objects.get(user=uid)
        except user_detail.DoesNotExist:
            profiledata = None

        manager = (userdata.user_type == "manager")

        return {
            'uid': uid,
            'userdata': userdata,
            'profiledata': profiledata,
            'manager': manager,
            'is_logged_in': True,
        }

    except Exception:
        # No session or invalid session — return safe empty context
        return {
            'uid': None,
            'userdata': None,
            'profiledata': None,
            'manager': False,
            'is_logged_in': False,
        }



def manager_required(request):
    uid = request.session.get('login_id')
    if not uid:
        messages.error(request, "Please log in to continue.")
        return redirect('/login')
    try:
        userdata = login.objects.get(id=uid)
        if userdata.user_type == 'admin':
            return redirect('/myadmin/dashboard')
        if userdata.is_banned:
            messages.error(request, "Your account has been banned. Please contact support.")
            return redirect('/login')
        if userdata.user_type != 'manager':
            messages.error(request, "Access denied. This section is for managers only.")
            return redirect('/index')
    except login.DoesNotExist:
        messages.error(request, "Please log in to continue.")
        return redirect('/login')
    return None


def user_required(request):
    uid = request.session.get('login_id')
    if not uid:
        messages.error(request, "Please log in to continue.")
        return redirect('/login')
    try:
        userdata = login.objects.get(id=uid)
        if userdata.user_type == 'admin':
            return redirect('/myadmin/dashboard')
        if userdata.is_banned:
            messages.error(request, "Your account has been banned. Please contact support.")
            return redirect('/login')
        if userdata.user_type == 'manager':
            messages.error(request, "Managers cannot access user booking pages. Please use the manager panel.")
            return redirect('/index')
    except login.DoesNotExist:
        messages.error(request, "Please log in to continue.")
        return redirect('/login')
    return None


def login_required(request):
    uid = request.session.get('login_id')
    if not uid:
        messages.error(request, "Please login first to access this page.")
        return redirect('/login')
    try:
        login.objects.get(id=uid)
    except login.DoesNotExist:
        messages.error(request, "Session expired. Please login again.")
        return redirect('/login')
    return None



def fetchturfs(request):
    uid = request.session['login_id']
    userdata = login.objects.get(id=uid)

    try:
        profiledata = user_detail.objects.get(user=uid)
    except user_detail.DoesNotExist:
        profiledata = None

    manager = False
    if userdata.user_type == "manager":
        manager = True

    if request.method == 'POST':
        t_areaname = request.POST.get('areaname')
        turfs = turf.objects.filter(Q(name__icontains=t_areaname) | Q(category__cate_name__icontains=t_areaname) | Q(
            location__area_name__icontains=t_areaname))

        if not turfs.exists():
            messages.error(request, "No result found for this category or location.")

        context = {
            'uid': uid,
            'userdata': userdata,
            'profiledata': profiledata,
            'manager': manager,
            'turfs': turfs
        }

        return render(request, 'index.html', context)


def register(request):
    return render(request, "register.html")


def forgotpasswordpage(request):
    context = checkuser(request)
    return render(request, "forgotpassword.html", context)


def forgotpassword(request):
    if request.method == 'POST':
        username = request.POST.get('email')

        try:
            user = login.objects.get(email=username)
        except login.DoesNotExist:
            user = None

        if user is not None:
            import random
            import time
            otp = str(random.randint(100000, 999999))
            request.session['otp'] = otp
            request.session['entered_email'] = username
            request.session['otp_time'] = str(time.time())
            request.session.save()

            msg = "Here is your OTP for password reset: " + otp
            from django.core.mail import send_mail
            send_mail(
                'Your OTP',
                msg,
                'easyturfsinfo@gmail.com',
                [username],
                fail_silently=False,
            )

            messages.success(request, 'OTP sent to your email')
            return redirect("verifyotppage")
        else:
            messages.error(request, 'This account does not exist')
            context = {'filled_email': username}
            return render(request, 'forgotpassword.html', context)
    return redirect("index")

def verifyotppage(request):
    import time
    otp_time = float(request.session.get('otp_time', 0))
    # If no OTP session is running, boot them out
    if otp_time == 0:
        return redirect("forgotpasswordpage")
        
    elapsed = time.time() - otp_time
    
    expires_in = int(300 - elapsed)
    resend_in = int(60 - elapsed)
    
    if expires_in < 0: expires_in = 0
    if resend_in < 0: resend_in = 0
    
    context = {'expires_in': expires_in, 'resend_in': resend_in, 'checkuser': checkuser(request)}
    return render(request, "verifyotp.html", context)

def verifyotp(request):
    if request.method == 'POST':
        import time
        entered_otp = request.POST.get("otp")
        saved_otp = request.session.get("otp")
        otp_time = float(request.session.get("otp_time", 0))
        
        if time.time() - otp_time > 300:
            if 'otp' in request.session: del request.session['otp']
            messages.error(request, 'OTP has expired, please request a new one.')
            return redirect("forgotpasswordpage")

        if entered_otp and saved_otp and entered_otp == saved_otp:
            request.session['otp_verified'] = True
            messages.success(request, 'OTP Verified successfully')
            return redirect("resetpasswordpage")
        else:
            messages.error(request, 'Invalid OTP, please try again')
            return redirect("verifyotppage")
    return redirect("index")
    
def resendotp(request):
    import time
    username = request.session.get('entered_email')
    otp_time = float(request.session.get('otp_time', 0))
    
    if not username:
        return redirect("forgotpasswordpage")
        
    if time.time() - otp_time < 60:
        messages.error(request, "Please wait before resending the OTP.")
        return redirect("verifyotppage")
        
    import random
    otp = str(random.randint(100000, 999999))
    request.session['otp'] = otp
    request.session['otp_time'] = str(time.time())
    if 'otp_verified' in request.session: del request.session['otp_verified']
    request.session.save()

    msg = "Here is your new OTP for password reset: " + otp
    from django.core.mail import send_mail
    send_mail(
        'Your New OTP',
        msg,
        'easyturfsinfo@gmail.com',
        [username],
        fail_silently=False,
    )
    
    messages.success(request, 'A new OTP has been sent to your email.')
    return redirect("verifyotppage")

def resetpasswordpage(request):
    if not request.session.get('otp_verified'):
        messages.error(request, 'Unauthorized access.')
        return redirect("forgotpasswordpage")
    return render(request, "resetpassword.html")

def resetpassword(request):
    if request.method == 'POST':
        pwd = request.POST.get("password")
        cpwd = request.POST.get("confirmpassword")
        email = request.session.get('entered_email')
        
        if pwd and cpwd and pwd == cpwd and email and request.session.get('otp_verified'):
            cuser = login.objects.get(email=email)
            cuser.password = pwd
            cuser.save(update_fields=['password'])
            
            try:
                del request.session['otp']
                del request.session['entered_email']
                del request.session['otp_time']
                del request.session['otp_verified']
            except KeyError:
                pass
            
            messages.success(request, "Password changed successfully")
            return redirect("login")
        else:
            messages.error(request, "Passwords do not match or invalid session")
            return redirect("resetpasswordpage")
    return redirect("index")


def createuser(request):
    try:
        if request.method == "POST":
            name = request.POST.get("name")
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            role = request.POST.get("role")
            password1 = request.POST.get("password")
            password2 = request.POST.get("confirmpassword")

            # Server Side Validations
            import re
            errors = []
            
            if len(name.strip()) <= 2:
                errors.append("Name must be at least 3 characters long.")
            if not phone.strip().isdigit():
                errors.append("Only accept numbers.")
            elif not re.match(r'^\d{10}$', phone.strip()):
                errors.append("Phone number must be exactly 10 digits.")
            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email.strip()):
                errors.append("Invalid email format.")
                
            pwd = password1
            if len(pwd) <= 6 or not re.search(r'[a-z]', pwd) or not re.search(r'[A-Z]', pwd) or not re.search(r'[0-9]', pwd) or not re.search(r'[@#$%^&*()_+!~`\-={}\[\]:;"\'<>,.?/\|\\]', pwd):
                errors.append("Password must be > 6 chars, with at least 1 lowercase, 1 uppercase, 1 number, and 1 symbol.")
                
            if password1 != password2:
                errors.append("Passwords do not match.")
                
            # Check if email is already taken
            if login.objects.filter(email=email).exists():
                errors.append("Email already exists, please use another email.")

            if errors:
                for error in errors:
                    messages.error(request, error)
                messages.error(request, "Please fill all required fields correctly!")
                context = {
                    'filled_name': name,
                    'filled_email': email,
                    'filled_phone': phone,
                    'filled_role': role,
                }
                return render(request, "register.html", context)

            registerdata = login(name=name, email=email, phone_number=phone, password=password1, user_type=role)
            registerdata.save()
            return redirect("login")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        context = {}
        if request.method == "POST":
            context = {
                'filled_name': request.POST.get("name", ""),
                'filled_email': request.POST.get("email", ""),
                'filled_phone': request.POST.get("phone", ""),
                'filled_role': request.POST.get("role", "user"),
            }
        return render(request, "register.html", context)
    
    return render(request, "register.html")


def userprofile(request):
    guard = login_required(request)
    if guard: return guard
    context = checkuser(request)
    return render(request, "user/userprofile.html", context)


def edituserprofile(request):
    guard = login_required(request)
    if guard: return guard
    context = checkuser(request)
    return render(request, "user/edituserprofile.html", context)


def updateprofile(request):
    guard = login_required(request)
    if guard: return guard
    context = checkuser(request)
    try:
        if request.method == "POST":
            if 'update' in request.POST:
                uid = request.session['login_id']
                userdata = login.objects.get(id=uid)
                profiledata = user_detail.objects.get(user=uid)

                name = request.POST.get("name")
                phone = request.POST.get("phone")
                email = request.POST.get("email")
                address = request.POST.get("address")

                userdata.name = name
                userdata.phone_number = phone
                userdata.email = email
                profiledata.address = address

                if 'profile' in request.FILES:
                    profile = request.FILES["profile"]
                    print(profile)
                    profiledata.profile_pic = profile

                userdata.save()
                profiledata.save()

                messages.success(request, 'Your profile has been updated successfully.')
                return redirect(userprofile)
            else:
                messages.success(request, 'Some error occurs.')
                return redirect(userprofile)

    except:
        pass

    return render(request, "user/userprofile.html", context)


def completeprofilepage(request):
    guard = user_required(request)
    if guard: return guard
    context = checkuser(request)
    return render(request, "user/completeprofile.html", context)


def completeprofile(request):
    guard = user_required(request)
    if guard: return guard
    try:
        uid = request.session['login_id']
        if request.method == "POST":
            dob = request.POST.get("dob")
            address = request.POST.get("address")
            profilepic = request.FILES["profile"]

            insertdata = user_detail(user=login(id=uid), address=address, profile_pic=profilepic, dob=dob)
            insertdata.save()

            messages.success(request, "profile completed successfully")
            return redirect(userprofile)

    except:
        pass

    return render(request, "index.html")


def index(request):
    context = checkuser(request)
    turfs = turf.objects.all()
    context.update({"turfs": turfs})
    return render(request, 'index.html', context)


def loginpage(request):
    return render(request, 'login.html')


def loginuser(request):
    if request.method == "POST":
        uemail = request.POST.get("email")
        upwd = request.POST.get("password")

        try:
            logindata = login.objects.get(email=uemail, password=upwd)
        except login.DoesNotExist:
            logindata = None

        if logindata is not None:
            if logindata.is_banned:
                messages.error(request, "Your account has been banned. Please contact support.")
                return render(request, 'login.html')
            request.session['login_id'] = logindata.id
            request.session.save()
            messages.success(request, "Login Successful!")
            if logindata.user_type == 'admin':
                return redirect('/myadmin/dashboard')
            return redirect('index')
        else:
            messages.error(request, "Invalid email or password.")
            return render(request, 'login.html')

    return render(request, 'login.html')


def logout(request):
    try:
        del request.session['login_id']
        del request.session['login_pwd']
    except:
        pass

    return redirect("index")


def changepwdpage(request):
    guard = login_required(request)
    if guard: return guard
    context = checkuser(request)
    return render(request, "user/changepwdpage.html", context)


def changepwd(request):
    guard = login_required(request)
    if guard: return guard
    context = checkuser(request)
    userdata = context.get("userdata")
    try:
        pwd = userdata.password

        if request.method == "POST":
            oldpwd = request.POST.get("oldpwd")
            newpwd = request.POST.get("newpwd")
            confirmpwd = request.POST.get("confirmpwd")

            if oldpwd == pwd:
                if newpwd == confirmpwd:
                    userdata.password = newpwd
                    userdata.save()
                    messages.success(request, 'Password Updated Successfully.')
                    del request.session['login_id']
                    return redirect(loginuser)
                else:
                    messages.error(request, "New Password and confirm not same")
                    return redirect(changepwdpage)
            else:
                messages.error(request, "Invalid Old Password")
                return redirect(changepwdpage)

    except userdata.DoesNotExist:
        messages.error(request, 'This account does not exist.')
        return redirect(index)

    return render(request, "index.html", context)


def services(request):
    context = checkuser(request)
    return render(request, "services.html", context)


def about(request):
    context = checkuser(request)
    return render(request, "about.html", context)


def contact(request):
    context = checkuser(request)
    return render(request, "contact.html", context)


def contactus(request):
    context = checkuser(request)
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        subject = request.POST.get("subject")
        message = request.POST.get("message")
        insert = inquiry(name=name, contact_number=phone, contact_email=email, subject=subject, description=message)
        insert.save()
    return render(request, 'index.html', context)


def userturflist(request):
    context = checkuser(request)
    try:
        turfs = turf.objects.all()
        context.update({"turfs": turfs})
        return render(request, 'user/userturflist.html', context)
    except Exception:
        pass
    return render(request, 'user/userturflist.html', context)


def turfdetails(request, id):
    context = checkuser(request)
    try:
        turfdata = turf.objects.get(id=id)
        context.update({"turfdata": turfdata})
    except Exception:
        messages.error(request, "Details do not exist.")
    return render(request, 'user/turfdetails.html', context)


def userbooking(request):
    return render(request, 'booking.html')


def selectdate(request, id):
    guard = user_required(request)
    if guard: return guard
    uid = request.session["login_id"]
    context = checkuser(request)

    try:
        profiledata = user_detail.objects.get(user=uid)
    except user_detail.DoesNotExist:
        profiledata = None
        messages.error(request, "Please complete your profile first")
        return redirect("/completeprofilepage")

    import datetime as dt
    today = date.today()
    now_time = dt.datetime.now().time()

    from django.db.models import Q

    available_dates_qs = (
        slot.objects
        .filter(
            turf=id,
            date__gte=today,
            is_booked=False,
            is_available=True,
        )
        .filter(
            Q(date__gt=today) | Q(date=today, start_time__gt=now_time)
        )
        .values('date')
        .annotate(total_slots=Count('id'))
        .filter(total_slots__gt=0)  
        .order_by('date')
    )

    try:
        turfdata = turf.objects.get(id=id)
    except turf.DoesNotExist:
        messages.error(request, "Turf not found")
        return redirect("/userturflist")

    context.update({
        "turfid": id,
        "turfdata": turfdata,
        "available_dates": available_dates_qs,
        "today": today,
    })
    return render(request, 'user/selectdate.html', context)


def selectslotpage(request):
    guard = user_required(request)
    if guard: return guard
    context = checkuser(request)

    if request.method == "POST":
        turfid = request.POST.get("turfid")
        userdate = request.POST.get("date")
        user_selected_date = datetime.strptime(userdate, "%Y-%m-%d").date()
        current_date = date.today()
        import datetime as dt
        now_time = dt.datetime.now().time()

        if user_selected_date < current_date:
            messages.error(request, "Selected date cannot be in the past")
            return redirect("/userturflist")

        if user_selected_date == current_date:
            slotsdata = slot.objects.filter(
                turf=turfid, date=userdate,
                is_available=True, start_time__gt=now_time
            ).order_by('start_time')
        else:
            slotsdata = slot.objects.filter(
                turf=turfid, date=userdate, is_available=True
            ).order_by('start_time')

        try:
            turfdata = turf.objects.get(id=turfid)
        except Exception:
            turfdata = None

        context.update({
            "slotsdata": slotsdata,
            "turfid": turfid,
            "selected_date": userdate,
            "turfdata": turfdata,
        })
    return render(request, 'user/selectslot.html', context)



def selectslot(request):
    guard = user_required(request)
    if guard: return guard
    context = checkuser(request)

    try:
        if request.method == 'POST':
            selected_slot_id = request.POST.get('selectedSlot')
            turfid = request.POST.get('turfid')
            if selected_slot_id is not None:
                context.update({"slotid": selected_slot_id, "turfid": turfid})
                return redirect("/initiate_payment")
            else:
                messages.error(request, "Please select a slot.")

    except:
        messages.error(request, "Some error occurred")
    return redirect("/userturflist")


import uuid
import razorpay
import hmac
import hashlib
from django.conf import settings as django_settings
from django.views.decorators.csrf import csrf_exempt


def initiate_payment(request):
    guard = user_required(request)
    if guard: return guard
    context = checkuser(request)
    uid = request.session.get('login_id')

    if request.method == "POST":
        turfid  = request.POST.get("turfid")
        slotid  = request.POST.get("selectedSlot")

        if not turfid or not slotid:
            messages.error(request, "Invalid booking request.")
            return redirect("/userturflist")

        try:
            turfdata = turf.objects.get(id=turfid)
            slotdata = slot.objects.get(id=slotid)
        except Exception:
            messages.error(request, "Turf or slot not found.")
            return redirect("/userturflist")

        if slotdata.is_booked:
            messages.error(request, "This slot is already booked. Please choose another.")
            return redirect(f"/selectdate/{turfid}")

        amount_inr  = turfdata.price_per_slot          
        amount_paise = amount_inr * 100                 

        client = razorpay.Client(
            auth=(django_settings.RAZORPAY_KEY_ID, django_settings.RAZORPAY_KEY_SECRET)
        )
        rz_order = client.order.create({
            "amount":   amount_paise,
            "currency": "INR",
            "payment_capture": 1,   
        })

        try:
            userdata = login.objects.get(id=uid)
        except Exception:
            userdata = None

        context.update({
            "turfdata":        turfdata,
            "slotdata":        slotdata,
            "amount_inr":      amount_inr,
            "razorpay_key":    django_settings.RAZORPAY_KEY_ID,
            "razorpay_order_id": rz_order["id"],
            "user_name":       userdata.name  if userdata else "",
            "user_email":      userdata.email if userdata else "",
            "user_phone":      userdata.phone_number if userdata else "",
            "turfid":          turfid,
            "slotid":          slotid,
        })
        return render(request, "user/razorpay_checkout.html", context)

    return redirect("/userturflist")


@csrf_exempt
def verify_payment(request):
    guard = user_required(request)
    if guard: return guard
    context = checkuser(request)
    uid = request.session.get('login_id')

    if request.method == "POST":
        rz_order_id   = request.POST.get("razorpay_order_id")
        rz_payment_id = request.POST.get("razorpay_payment_id")
        rz_signature  = request.POST.get("razorpay_signature")
        turfid        = request.POST.get("turfid")
        slotid        = request.POST.get("slotid")

        # ── Signature verification ───────────────────────────
        key_secret = django_settings.RAZORPAY_KEY_SECRET.encode()
        msg        = f"{rz_order_id}|{rz_payment_id}".encode()
        generated  = hmac.new(key_secret, msg, hashlib.sha256).hexdigest()

        if generated != rz_signature:
            messages.error(request, "Payment verification failed. Please contact support.")
            return redirect("/userturflist")

        try:
            turfdata = turf.objects.get(id=turfid)
            slotdata = slot.objects.get(id=slotid)

            slotdata.is_booked = True
            slotdata.save()

            new_booking = booking(
                user=login(id=uid),
                turf=turfdata,
                slot=slotdata,
                booking_status="booked"
            )
            new_booking.save()

            new_payment = payment(
                user=login(id=uid),
                booking=new_booking,
                amount=turfdata.price_per_slot,
                payment_method="Razorpay",
                transaction_id=rz_payment_id,
                payment_status="complete"
            )
            new_payment.save()

            messages.success(request, "Payment successful! Your turf is booked.")
            return redirect("/payment_success")

        except Exception as e:
            messages.error(request, f"Booking could not be saved: {str(e)}")
            return redirect("/userturflist")

    return redirect("/userturflist")


def payment_success(request):
    guard = user_required(request)
    if guard: return guard
    context = checkuser(request)
    return render(request, "user/payment_success.html", context)



def userpayemnts(request):
    guard = user_required(request)
    if guard: return guard
    context = checkuser(request)
    try:
        uid = request.session['login_id']
        paymentdata = payment.objects.filter(user=uid)

        page = request.GET.get('page', 1)
        paginator = Paginator(paymentdata, 2)  

        try:
            paymentdata = paginator.page(page)
        except PageNotAnInteger:
            paymentdata = paginator.page(1)
        except EmptyPage:
            paymentdata = paginator.page(paginator.num_pages)

        context.update({'paginator': paginator, 'page': int(page), 'paymentdata': paymentdata})

        return render(request, "user/userpayments.html", context)
    except:
        pass

    return render(request, "index.html")


def userbookings(request):
    guard = user_required(request)
    if guard: return guard
    context = checkuser(request)
    uid = request.session['login_id']
    import datetime as dt
    now_dt = dt.datetime.now()          
    bookingdata = booking.objects.filter(user=login(id=uid)).order_by('-booked_at')
    cdate = date.today()
    page = request.GET.get('page', 1)
    paginator = Paginator(bookingdata, 10)

    try:
        bookingdata = paginator.page(page)
    except PageNotAnInteger:
        bookingdata = paginator.page(1)
    except EmptyPage:
        bookingdata = paginator.page(paginator.num_pages)

    context.update({'paginator': paginator, 'page': int(page), 'bookingdata': bookingdata,
                     'cdate': cdate, 'now_dt': now_dt})
    return render(request, "user/userbookings.html", context)


def addturfpage(request):
    guard = manager_required(request)
    if guard: return guard
    context = checkuser(request)
    uid = request.session["login_id"]
    try:
        profiledata = user_detail.objects.get(user=uid)
    except user_detail.DoesNotExist:
        profiledata = None
        messages.error(request, "please complete your profile")
        return redirect("/completeprofilepage")

    categories = turf_categories.objects.all()
    locations = location.objects.all()
    context.update({'categories': categories, 'locations': locations})
    return render(request, "manager/addturf.html", context)


def addturf(request):
    guard = manager_required(request)
    if guard: return guard
    context = checkuser(request)
    uid = request.session.get("login_id")

    if request.method == "POST":
        import re
        manager_id = request.POST.get("manager")
        category   = request.POST.get("category")
        loc        = request.POST.get("location")
        turfname   = request.POST.get("name", "").strip()
        desc       = request.POST.get("description", "").strip()
        phone      = request.POST.get("contact_number", "").strip()
        email      = request.POST.get("contact_email", "").strip()
        price      = request.POST.get("price_per_slot", "").strip()
        capacity   = request.POST.get("maximum_capacity", "").strip()
        rules      = request.POST.get("rules", "").strip()
        duration   = request.POST.get("duration", "").strip()
        image      = request.FILES.get("image")

        errors = []

        if len(turfname) < 3:
            errors.append("Turf name must be at least 3 characters.")
        if len(desc) < 10:
            errors.append("Description must be at least 10 characters.")
        if not category:
            errors.append("Please select a category.")
        if not loc:
            errors.append("Please select a location.")
        if not phone.isdigit() or len(phone) != 10:
            errors.append("Contact number must be exactly 10 digits.")
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            errors.append("Invalid contact email.")
        try:
            price_val = int(price)
            if price_val <= 0:
                errors.append("Price per slot must be a positive number.")
        except (ValueError, TypeError):
            errors.append("Price per slot must be a valid number.")
        try:
            capacity_val = int(capacity)
            if capacity_val <= 0:
                errors.append("Maximum capacity must be a positive number.")
        except (ValueError, TypeError):
            errors.append("Maximum capacity must be a valid number.")
        try:
            duration_val = int(duration)
            if duration_val <= 0:
                errors.append("Duration per slot must be a positive number.")
        except (ValueError, TypeError):
            errors.append("Duration per slot must be a valid number.")

        if errors:
            for error in errors:
                messages.error(request, error)
            categories = turf_categories.objects.all()
            locations  = location.objects.all()
            context.update({
                'categories': categories, 'locations': locations,
                'filled': request.POST,
            })
            return render(request, "manager/addturf.html", context)

        new_turf = turf(
            manager=login(id=manager_id),
            category=turf_categories(id=category),
            location=location(id=loc),
            name=turfname,
            description=desc,
            contact_number=phone,
            contact_email=email,
            price_per_slot=price_val,
            duration_per_slot=duration_val,
            maximum_capacity=capacity_val,
            rules_and_regulations=rules if rules else None,
        )
        if image:
            new_turf.image = image
        new_turf.save()
        messages.success(request, "Turf added successfully!")
        return redirect("/turflist")

    return redirect("/addturfpage")



def turflist(request):
    guard = manager_required(request)
    if guard: return guard
    uid = request.session["login_id"]
    context = checkuser(request)
    turfdata = turf.objects.filter(manager=login(id=uid))
    page = request.GET.get('page', 1)
    paginator = Paginator(turfdata, 6)  
    try:
        turfdata = paginator.page(page)
    except PageNotAnInteger:
        turfdata = paginator.page(1)
    except EmptyPage:
        turfdata = paginator.page(paginator.num_pages)

    context.update({'paginator': paginator, 'page': int(page), 'turfdata': turfdata})

    return render(request, "manager/turflist.html", context)


def addimages(request):
    return redirect("/turflist")


def addphotossubmit(request):
    return redirect("/turflist")



def timeslots(request):
    guard = manager_required(request)
    if guard: return guard
    context = checkuser(request)
    uid = request.session["login_id"]
    try:
        profiledata = user_detail.objects.get(user=uid)
    except user_detail.DoesNotExist:
        profiledata = None
        messages.error(request, "please complete your profile")
        return redirect("/completeprofilepage")

    turfdata = turf.objects.filter(manager=login(id=uid))
    context.update({'turfdata': turfdata})
    return render(request, "manager/timeslots.html", context)


def saveslot(request):
    guard = manager_required(request)
    if guard: return guard
    context = checkuser(request)
    try:
        if request.method == "POST":
            import datetime as dt
            turfid    = request.POST.get("turfid")
            userdate  = request.POST.get("date")
            startTime = request.POST.get("startTime")
            endTime   = request.POST.get("endTime")

            errors = []
            if not turfid or turfid == "#":
                errors.append("Please select a turf.")
            if not userdate:
                errors.append("Please select a date.")
            if not startTime:
                errors.append("Please enter a start time.")
            if not endTime:
                errors.append("Please enter an end time.")
            if startTime and endTime and startTime >= endTime:
                errors.append("Start time must be before end time.")

            if errors:
                for error in errors:
                    messages.error(request, error)
                return redirect("/timeslots")

            user_selected_date = dt.datetime.strptime(userdate, "%Y-%m-%d").date()
            current_date = dt.date.today()
            now_time = dt.datetime.now().time()
            start_time_obj = dt.datetime.strptime(startTime, "%H:%M").time()

            if user_selected_date < current_date:
                messages.error(request, "Selected date cannot be in the past.")
                return redirect("/timeslots")

            if user_selected_date == current_date and start_time_obj <= now_time:
                messages.error(request, f"Cannot add a slot starting at {startTime} — that time has already passed today.")
                return redirect("/timeslots")

            is_avail = True
            if user_selected_date == current_date and start_time_obj <= now_time:
                is_avail = False

            insertslot = slot(
                turf=turf(id=turfid),
                date=user_selected_date,
                start_time=startTime,
                end_time=endTime,
                is_available=is_avail
            )
            insertslot.save()
            messages.success(request, "Slot added successfully!")
            return redirect("/viewslots")

    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("/timeslots")


def viewslots(request):
    guard = manager_required(request)
    if guard: return guard
    context = checkuser(request)
    uid = request.session["login_id"]

    import datetime as dt
    now = dt.datetime.now()
    slot.objects.filter(
        is_available=True,
        date__lt=now.date()
    ).update(is_available=False)
    slot.objects.filter(
        is_available=True,
        date=now.date(),
        start_time__lte=now.time()
    ).update(is_available=False)

    turfdata = turf.objects.filter(manager=login(id=uid))
    turf_ids = turfdata.values_list('id', flat=True)
    slotsdata = slot.objects.filter(turf__in=turf_ids).order_by('-date', 'start_time')

    page = request.GET.get('page', 1)
    paginator = Paginator(slotsdata, 10)
    try:
        slotsdata = paginator.page(page)
    except PageNotAnInteger:
        slotsdata = paginator.page(1)
    except EmptyPage:
        slotsdata = paginator.page(paginator.num_pages)

    context.update({'paginator': paginator, 'page': int(page), 'slotsdata': slotsdata})
    return render(request, "manager/viewslots.html", context)


def editturfpage(request, id):
    guard = manager_required(request)
    if guard: return guard
    context = checkuser(request)
    turfdata = turf.objects.get(id=id)
    categories = turf_categories.objects.all()
    locations = location.objects.all()
    context.update({'turfdata': turfdata, 'categories': categories, 'locations': locations})
    return render(request, "manager/editturfs.html", context)


def updateturf(request, id):
    guard = manager_required(request)
    if guard: return guard
    try:
        if request.method == "POST":
            import re
            uid = request.session['login_id']
            turfdata = turf.objects.get(id=id, manager=login(id=uid))

            name     = request.POST.get("name", "").strip()
            desc     = request.POST.get("description", "").strip()
            category = request.POST.get("category")
            loc      = request.POST.get("location")
            phone    = request.POST.get("contact_number", "").strip()
            email    = request.POST.get("contact_email", "").strip()
            price    = request.POST.get("price_per_slot", "").strip()
            capacity = request.POST.get("maximum_capacity", "").strip()
            rules    = request.POST.get("rules", "").strip()
            image    = request.FILES.get("image")

            errors = []
            if len(name) < 3:
                errors.append("Turf name must be at least 3 characters.")
            if len(desc) < 10:
                errors.append("Description must be at least 10 characters.")
            if not phone.isdigit() or len(phone) != 10:
                errors.append("Contact number must be exactly 10 digits.")
            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                errors.append("Invalid contact email.")
            try:
                price_val = int(price)
                if price_val <= 0:
                    errors.append("Price per slot must be a positive number.")
            except (ValueError, TypeError):
                errors.append("Price per slot must be a valid number.")
            try:
                capacity_val = int(capacity)
                if capacity_val <= 0:
                    errors.append("Maximum capacity must be a positive number.")
            except (ValueError, TypeError):
                errors.append("Maximum capacity must be a valid number.")

            if errors:
                for error in errors:
                    messages.error(request, error)
                context = checkuser(request)
                categories = turf_categories.objects.all()
                locations  = location.objects.all()
                context.update({'turfdata': turfdata, 'categories': categories, 'locations': locations})
                return render(request, "manager/editturfs.html", context)

            turfdata.name = name
            turfdata.description = desc
            turfdata.contact_number = phone
            turfdata.contact_email = email
            turfdata.price_per_slot = price_val
            turfdata.maximum_capacity = capacity_val
            turfdata.rules_and_regulations = rules if rules else None
            turfdata.location = location(id=loc)
            turfdata.category = turf_categories(id=category)
            if image:
                turfdata.image = image

            turfdata.save()
            messages.success(request, 'Turf updated successfully.')
            return redirect("/turflist")
        else:
            return redirect("/turflist")

    except Exception as e:
        messages.error(request, f"Error updating turf: {str(e)}")

    return redirect("/turflist")


def removeturf(request, id):
    guard = manager_required(request)
    if guard: return guard
    context = checkuser(request)
    try:
        turdata = turf.objects.get(id=id)
        turdata.delete()
        messages.success(request, "Turf removed successfully !!")
        return redirect(turflist)
    except:
        pass
    return render(request, "index.html", context)


def removeslot(request, id):
    guard = manager_required(request)
    if guard: return guard
    context = checkuser(request)
    try:
        slotdata = slot.objects.get(id=id)
        slotdata.delete()
        messages.success(request, "slot removed successfully !!")
        return redirect(viewslots)
    except:
        messages.error(request, "slot data does not exist")
    return redirect("/viewslots")


def turfbookings(request):
    guard = manager_required(request)
    if guard: return guard
    context = checkuser(request)
    uid = request.session['login_id']
    my_turf_ids = turf.objects.filter(manager=login(id=uid)).values_list('id', flat=True)
    bookingdata = booking.objects.filter(turf__id__in=my_turf_ids).order_by('-booked_at')

    page = request.GET.get('page', 1)
    paginator = Paginator(bookingdata, 10)
    try:
        bookingdata = paginator.page(page)
    except PageNotAnInteger:
        bookingdata = paginator.page(1)
    except EmptyPage:
        bookingdata = paginator.page(paginator.num_pages)

    context.update({'paginator': paginator, 'page': int(page), 'bookingdata': bookingdata})
    return render(request, "manager/turfbookings.html", context)


def turfpayments(request):
    guard = manager_required(request)
    if guard: return guard
    context = checkuser(request)
    uid = request.session['login_id']
    my_turf_ids = turf.objects.filter(manager=login(id=uid)).values_list('id', flat=True)
    paymentsdata = payment.objects.filter(booking__turf__id__in=my_turf_ids).order_by('-payment_date_time')

    page = request.GET.get('page', 1)
    paginator = Paginator(paymentsdata, 10)
    try:
        paymentsdata = paginator.page(page)
    except PageNotAnInteger:
        paymentsdata = paginator.page(1)
    except EmptyPage:
        paymentsdata = paginator.page(paginator.num_pages)

    context.update({'paginator': paginator, 'page': int(page), 'paymentsdata': paymentsdata})
    return render(request, "manager/turfpayments.html", context)


def feedbacks(request, fid):
    guard = user_required(request)
    if guard: return guard
    context = checkuser(request)
    uid = request.session['login_id']
    try:
        turfdata = turf.objects.get(id=fid)
    except turf.DoesNotExist:
        messages.error(request, "Turf not found.")
        return redirect('/userbookings')
    has_booking = booking.objects.filter(
        user=login(id=uid), turf=turfdata, booking_status='booked'
    ).exists()
    if not has_booking:
        messages.error(request, "You can only leave feedback for turfs you have booked.")
        return redirect('/userbookings')
    existing = feedback.objects.filter(user=login(id=uid), turf=turfdata).first()
    context.update({'fid': fid, 'turfdata': turfdata, 'existing': existing})
    return render(request, 'user/feedback.html', context)


def addfeedback(request):
    guard = user_required(request)
    if guard: return guard
    if request.method != "POST":
        return redirect('/userbookings')
    uid = request.session['login_id']
    tid = request.POST.get("fid", "").strip()
    message = request.POST.get("message", "").strip()
    rating_raw = request.POST.get("rating", "0").strip()
    try:
        turfdata = turf.objects.get(id=tid)
    except (turf.DoesNotExist, ValueError):
        messages.error(request, "Invalid turf.")
        return redirect('/userbookings')
    try:
        rating_val = int(rating_raw)
        if not (1 <= rating_val <= 5):
            raise ValueError
    except (ValueError, TypeError):
        messages.error(request, "Please select a rating between 1 and 5.")
        return redirect(f'/feedback/{tid}')
    if len(message) < 5:
        messages.error(request, "Please write at least 5 characters in your feedback.")
        return redirect(f'/feedback/{tid}')
    fb_obj, created = feedback.objects.get_or_create(
        user=login(id=uid), turf=turfdata,
        defaults={'comment': message, 'rating': rating_val}
    )
    if not created:
        fb_obj.comment = message
        fb_obj.rating = rating_val
        fb_obj.save()
    messages.success(request, 'Thank you for your feedback!')
    return redirect('/userbookings')