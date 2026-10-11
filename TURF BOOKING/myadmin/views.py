from django.shortcuts import render, redirect
from django.contrib import messages
from turf.models import (
    login, user_detail, state, city, location, turf_categories,
    turf, slot, booking, payment, feedback, inquiry
)
import datetime


def admin_required(request):
    uid = request.session.get('login_id')
    if not uid:
        messages.error(request, "Please login to access the admin panel.")
        return redirect('/login')
    try:
        userdata = login.objects.get(id=uid)
        if userdata.user_type != 'admin':
            messages.error(request, "Access denied. Admins only.")
            return redirect('/index')
    except login.DoesNotExist:
        messages.error(request, "Session expired. Please login again.")
        return redirect('/login')
    return None


def get_admin_context(request):
    uid = request.session.get('login_id')
    try:
        userdata = login.objects.get(id=uid)
    except Exception:
        userdata = None
    return {'admin_user': userdata}


# ─── Dashboard ────────────────────────────────────────────────────────────────
def dashboard(request):
    guard = admin_required(request)
    if guard: return guard
    context = get_admin_context(request)
    context.update({
        'total_users':    login.objects.filter(user_type='user').count(),
        'total_managers': login.objects.filter(user_type='manager').count(),
        'total_turfs':    turf.objects.count(),
        'total_slots':    slot.objects.count(),
        'total_bookings': booking.objects.count(),
        'total_payments': payment.objects.count(),
        'total_feedback': feedback.objects.count(),
        'total_inquiries':inquiry.objects.filter(status='pending').count(),
        'recent_bookings':booking.objects.order_by('-booked_at')[:6],
        'recent_inquiries':inquiry.objects.order_by('-timestamp')[:5],
    })
    return render(request, 'admin/dashboard.html', context)


# ─── States ───────────────────────────────────────────────────────────────────
def view_states(request):
    guard = admin_required(request)
    if guard: return guard
    context = get_admin_context(request)
    context['states'] = state.objects.all().order_by('state_name')
    return render(request, 'admin/states.html', context)

def add_state(request):
    guard = admin_required(request)
    if guard: return guard
    if request.method == 'POST':
        name = request.POST.get('state_name', '').strip()
        if not name:
            messages.error(request, "State name cannot be empty.")
        elif state.objects.filter(state_name__iexact=name).exists():
            messages.error(request, "This state already exists.")
        else:
            state(state_name=name).save()
            messages.success(request, f'State "{name}" added successfully.')
        return redirect('/myadmin/states')
    return redirect('/myadmin/states')

def edit_state(request, sid):
    guard = admin_required(request)
    if guard: return guard
    try:
        s = state.objects.get(id=sid)
    except state.DoesNotExist:
        messages.error(request, "State not found.")
        return redirect('/myadmin/states')
    if request.method == 'POST':
        name = request.POST.get('state_name', '').strip()
        if not name:
            messages.error(request, "State name cannot be empty.")
        else:
            s.state_name = name
            s.save()
            messages.success(request, "State updated successfully.")
        return redirect('/myadmin/states')
    context = get_admin_context(request)
    context['edit_state'] = s
    context['states'] = state.objects.all().order_by('state_name')
    return render(request, 'admin/states.html', context)

def delete_state(request, sid):
    guard = admin_required(request)
    if guard: return guard
    try:
        state.objects.get(id=sid).delete()
        messages.success(request, "State deleted.")
    except state.DoesNotExist:
        messages.error(request, "State not found.")
    return redirect('/myadmin/states')


# ─── Cities ───────────────────────────────────────────────────────────────────
def view_cities(request):
    guard = admin_required(request)
    if guard: return guard
    context = get_admin_context(request)
    context['cities'] = city.objects.select_related('state_name').order_by('city_name')
    context['states'] = state.objects.all().order_by('state_name')
    return render(request, 'admin/cities.html', context)

def add_city(request):
    guard = admin_required(request)
    if guard: return guard
    if request.method == 'POST':
        cname = request.POST.get('city_name', '').strip()
        state_id = request.POST.get('state_id')
        if not cname or not state_id:
            messages.error(request, "City name and state are required.")
        else:
            try:
                s = state.objects.get(id=state_id)
                city(city_name=cname, state_name=s).save()
                messages.success(request, f'City "{cname}" added.')
            except state.DoesNotExist:
                messages.error(request, "Selected state not found.")
    return redirect('/myadmin/cities')

def edit_city(request, cid):
    guard = admin_required(request)
    if guard: return guard
    try:
        c = city.objects.get(id=cid)
    except city.DoesNotExist:
        messages.error(request, "City not found.")
        return redirect('/myadmin/cities')
    if request.method == 'POST':
        cname = request.POST.get('city_name', '').strip()
        state_id = request.POST.get('state_id')
        if not cname or not state_id:
            messages.error(request, "All fields are required.")
        else:
            try:
                s = state.objects.get(id=state_id)
                c.city_name = cname
                c.state_name = s
                c.save()
                messages.success(request, "City updated successfully.")
            except state.DoesNotExist:
                messages.error(request, "State not found.")
        return redirect('/myadmin/cities')
    context = get_admin_context(request)
    context['edit_city'] = c
    context['cities'] = city.objects.select_related('state_name').order_by('city_name')
    context['states'] = state.objects.all().order_by('state_name')
    return render(request, 'admin/cities.html', context)

def delete_city(request, cid):
    guard = admin_required(request)
    if guard: return guard
    try:
        city.objects.get(id=cid).delete()
        messages.success(request, "City deleted.")
    except city.DoesNotExist:
        messages.error(request, "City not found.")
    return redirect('/myadmin/cities')


# ─── Locations ────────────────────────────────────────────────────────────────
def view_locations(request):
    guard = admin_required(request)
    if guard: return guard
    context = get_admin_context(request)
    context['locations'] = location.objects.select_related('city_name', 'city_name__state_name').order_by('area_name')
    context['cities'] = city.objects.select_related('state_name').order_by('city_name')
    return render(request, 'admin/locations.html', context)

def add_location(request):
    guard = admin_required(request)
    if guard: return guard
    if request.method == 'POST':
        area = request.POST.get('area_name', '').strip()
        postal = request.POST.get('postal_code', '').strip()
        city_id = request.POST.get('city_id')
        if not area or not postal or not city_id:
            messages.error(request, "All fields are required.")
        else:
            try:
                c = city.objects.get(id=city_id)
                location(area_name=area, postal_code=postal, city_name=c).save()
                messages.success(request, f'Location "{area}" added.')
            except city.DoesNotExist:
                messages.error(request, "Selected city not found.")
    return redirect('/myadmin/locations')

def edit_location(request, lid):
    guard = admin_required(request)
    if guard: return guard
    try:
        loc = location.objects.get(id=lid)
    except location.DoesNotExist:
        messages.error(request, "Location not found.")
        return redirect('/myadmin/locations')
    if request.method == 'POST':
        area = request.POST.get('area_name', '').strip()
        postal = request.POST.get('postal_code', '').strip()
        city_id = request.POST.get('city_id')
        if not area or not postal or not city_id:
            messages.error(request, "All fields are required.")
        else:
            try:
                c = city.objects.get(id=city_id)
                loc.area_name = area
                loc.postal_code = postal
                loc.city_name = c
                loc.save()
                messages.success(request, "Location updated.")
            except city.DoesNotExist:
                messages.error(request, "City not found.")
        return redirect('/myadmin/locations')
    context = get_admin_context(request)
    context['edit_location'] = loc
    context['locations'] = location.objects.select_related('city_name__state_name').order_by('area_name')
    context['cities'] = city.objects.select_related('state_name').order_by('city_name')
    return render(request, 'admin/locations.html', context)

def delete_location(request, lid):
    guard = admin_required(request)
    if guard: return guard
    try:
        location.objects.get(id=lid).delete()
        messages.success(request, "Location deleted.")
    except location.DoesNotExist:
        messages.error(request, "Location not found.")
    return redirect('/myadmin/locations')


# ─── Turf Categories ──────────────────────────────────────────────────────────
def view_categories(request):
    guard = admin_required(request)
    if guard: return guard
    context = get_admin_context(request)
    context['categories'] = turf_categories.objects.all().order_by('cate_name')
    return render(request, 'admin/categories.html', context)

def add_category(request):
    guard = admin_required(request)
    if guard: return guard
    if request.method == 'POST':
        name = request.POST.get('cate_name', '').strip()
        if not name:
            messages.error(request, "Category name cannot be empty.")
        elif turf_categories.objects.filter(cate_name__iexact=name).exists():
            messages.error(request, "This category already exists.")
        else:
            turf_categories(cate_name=name).save()
            messages.success(request, f'Category "{name}" added.')
    return redirect('/myadmin/categories')

def edit_category(request, cid):
    guard = admin_required(request)
    if guard: return guard
    try:
        cat = turf_categories.objects.get(id=cid)
    except turf_categories.DoesNotExist:
        messages.error(request, "Category not found.")
        return redirect('/myadmin/categories')
    if request.method == 'POST':
        name = request.POST.get('cate_name', '').strip()
        if not name:
            messages.error(request, "Category name cannot be empty.")
        else:
            cat.cate_name = name
            cat.save()
            messages.success(request, "Category updated.")
        return redirect('/myadmin/categories')
    context = get_admin_context(request)
    context['edit_category'] = cat
    context['categories'] = turf_categories.objects.all().order_by('cate_name')
    return render(request, 'admin/categories.html', context)

def delete_category(request, cid):
    guard = admin_required(request)
    if guard: return guard
    try:
        turf_categories.objects.get(id=cid).delete()
        messages.success(request, "Category deleted.")
    except turf_categories.DoesNotExist:
        messages.error(request, "Category not found.")
    return redirect('/myadmin/categories')


# ─── Read-Only Views ──────────────────────────────────────────────────────────
def view_turfs(request):
    guard = admin_required(request)
    if guard: return guard
    context = get_admin_context(request)
    context['turfs'] = turf.objects.select_related('manager', 'category', 'location').order_by('-id')
    return render(request, 'admin/turfs.html', context)

def view_slots(request):
    guard = admin_required(request)
    if guard: return guard
    context = get_admin_context(request)
    context['slots'] = slot.objects.select_related('turf').order_by('-date', 'start_time')
    return render(request, 'admin/slots.html', context)

def view_bookings(request):
    guard = admin_required(request)
    if guard: return guard
    context = get_admin_context(request)
    context['bookings'] = booking.objects.select_related('user', 'turf', 'slot').order_by('-booked_at')
    return render(request, 'admin/bookings.html', context)

def view_feedbacks(request):
    guard = admin_required(request)
    if guard: return guard
    context = get_admin_context(request)
    context['feedbacks'] = feedback.objects.select_related('user', 'turf').order_by('-timestamp')
    return render(request, 'admin/feedbacks.html', context)

def view_inquiries(request):
    guard = admin_required(request)
    if guard: return guard
    context = get_admin_context(request)
    context['inquiries'] = inquiry.objects.all().order_by('-timestamp')
    return render(request, 'admin/inquiries.html', context)

def resolve_inquiry(request, iid):
    guard = admin_required(request)
    if guard: return guard
    try:
        inq = inquiry.objects.get(id=iid)
        inq.status = 'resolved' if inq.status == 'pending' else 'pending'
        inq.save()
        messages.success(request, f"Inquiry marked as {inq.status}.")
    except inquiry.DoesNotExist:
        messages.error(request, "Inquiry not found.")
    return redirect('/myadmin/inquiries')


# ─── Users ────────────────────────────────────────────────────────────────────
def view_users(request):
    guard = admin_required(request)
    if guard: return guard
    context = get_admin_context(request)
    users = login.objects.exclude(user_type='admin').order_by('user_type', 'name')
    context['users'] = users
    return render(request, 'admin/users.html', context)

def toggle_ban(request, uid):
    guard = admin_required(request)
    if guard: return guard
    try:
        u = login.objects.get(id=uid)
        if u.user_type == 'admin':
            messages.error(request, "Cannot ban another admin.")
            return redirect('/myadmin/users')
        u.is_banned = not u.is_banned
        u.save()
        status = "banned" if u.is_banned else "unbanned"
        messages.success(request, f'User "{u.name}" has been {status}.')
    except login.DoesNotExist:
        messages.error(request, "User not found.")
    return redirect('/myadmin/users')
