from django.urls import path

from . import views

from django.contrib.auth import views as auth_views
# app_name ='users'
urlpatterns = [
    path('',views.landing_page, name='landing_page'),
    path('logout/',auth_views.LogoutView.as_view(),name="logout"),
    path('agent_signup/',views.agent_signup_view,name="agent_signup"),
    path('tenant_signup/',views.tenant_signup_view,name="tenant_signup"),
    path('login/',views.login_view,name="login"),
    path('tenant_home/',views.tenant_home,name="tenant_home"),
    path('agent_home/',views.agent_home,name="agent_home"),
    path('agent_home/property/<int:id>/', views.property_details, name='property_details'),
    path('logout/',auth_views.LogoutView.as_view(),name="logout"),
    path('create_property/',views.create_property,name="create_property"),
    path('create_room/', views.create_room, name='create_room'),
    path('search_results/', views.search_results, name='search_results'),
    
    

]
