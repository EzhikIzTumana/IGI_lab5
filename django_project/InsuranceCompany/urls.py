"""
URL configuration for InsuranceCompany project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from catalog.views import *
from catalog import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),
    path('catalog/', include('catalog.urls')),
    path('faqs/', views.faqs, name='faqs'),
    path('', RedirectView.as_view(url='/home/', permanent=True)),
    path('departments/', views.department_list, name='department_list'),
    path('insurance-types/', views.insurance_type_list, name='insurance_type_list'),
    path('promos/', views.promo_list, name='promo_list'),
    path('contacts/', agent_list, name='contacts'),

    path('privacy-policy', views.privacy_policy, name='privacy_policy'),
    path('vacancies/', views.vacancies, name='vacancies'),
    path('reviews/', views.reviews, name='reviews'),
    path('review/create/', views.ReviewCreateView.as_view(), name='add_review'),
    path('review/<int:review_id>/edit/', views.ReviewEditView.as_view(), name='edit_review'),
    path('review/<int:review_id>/delete/', views.ReviewDeleteView.as_view(), name='delete_review'),

    re_path(r'^dashboard/$', views.dashboard, name='dashboard'),
    re_path(r'^dashboard/new-contract/$', views.new_contract, name='new_contract'),
    path('dashboard/new-policy/', views.new_policy, name='new_policy'),
    path('dashboard/policy-list/', views.policy_list, name='policy_list'),
    path('dashboard/contracts/', views.contract_list, name='contract_list'),
    path('dashboard/contracts/<int:contract_id>/edit/', edit_contract, name='edit_contract'),
    path('dashboard/contracts/<int:contract_id>/delete/', delete_contract, name='delete_contract'),
    path('dashboard/contract_search/', views.search_contracts, name='contract_search'),
    
    

    path('dashboard/agents/', views.agent_list, name='agent_list'),
    path('dashboard/agent-salaries/', views.agent_salary_list, name='agent_salary_list'),

    path('logout/', auth_views.LogoutView.as_view(next_page='/home/'), name='logout'),  # Redirect to home page after logout
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('news/', views.news, name='news'),
    path('about/', views.about_company, name='about'),
    path('dog_breeds/', views.dog_breeds, name='dog_breeds'),
    path('joke/', views.joke, name='joke'),
    path('visualization/', views.visualize_clients_employees, name='visualize_clients_employees'),
    path('statistics/', views.calculate_statistics, name='statistics'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

