from django.urls import path
from . import views

urlpatterns = [
    path('dashboard',               views.dashboard,        name='admin_dashboard'),

    # States
    path('states',                  views.view_states,      name='admin_states'),
    path('states/add',              views.add_state,        name='admin_add_state'),
    path('states/edit/<int:sid>',   views.edit_state,       name='admin_edit_state'),
    path('states/delete/<int:sid>', views.delete_state,     name='admin_delete_state'),

    # Cities
    path('cities',                  views.view_cities,      name='admin_cities'),
    path('cities/add',              views.add_city,         name='admin_add_city'),
    path('cities/edit/<int:cid>',   views.edit_city,        name='admin_edit_city'),
    path('cities/delete/<int:cid>', views.delete_city,      name='admin_delete_city'),

    # Locations
    path('locations',                   views.view_locations,   name='admin_locations'),
    path('locations/add',               views.add_location,     name='admin_add_location'),
    path('locations/edit/<int:lid>',    views.edit_location,    name='admin_edit_location'),
    path('locations/delete/<int:lid>',  views.delete_location,  name='admin_delete_location'),

    # Categories
    path('categories',                  views.view_categories,  name='admin_categories'),
    path('categories/add',              views.add_category,     name='admin_add_category'),
    path('categories/edit/<int:cid>',   views.edit_category,    name='admin_edit_category'),
    path('categories/delete/<int:cid>', views.delete_category,  name='admin_delete_category'),

    # Read-only views
    path('turfs',       views.view_turfs,       name='admin_turfs'),
    path('slots',       views.view_slots,        name='admin_slots'),
    path('bookings',    views.view_bookings,     name='admin_bookings'),
    path('feedbacks',   views.view_feedbacks,    name='admin_feedbacks'),
    path('inquiries',   views.view_inquiries,    name='admin_inquiries'),
    path('inquiries/resolve/<int:iid>', views.resolve_inquiry, name='admin_resolve_inquiry'),

    # Users
    path('users',                   views.view_users,   name='admin_users'),
    path('users/ban/<int:uid>',     views.toggle_ban,   name='admin_toggle_ban'),
]
