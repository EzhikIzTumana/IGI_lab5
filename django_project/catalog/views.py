from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, auth
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from .forms import RegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView
from .models import *
from .forms import *
from django.http import HttpResponseForbidden
from django.db.models import Avg, Count
import numpy as np
import matplotlib.pyplot as plt

from django.views.generic import *
import os
import matplotlib.pyplot as plt
from django.conf import settings
import requests
import logging

logging.basicConfig(level=logging.INFO, filename='logs.log', filemode='a',
                    format='%(asctime)s %(levelname)s %(message)s')

def home(request):
    latest_article = Article.objects.latest('date')
    logging.info(f'latest article title: {latest_article.title}')
    return render(request, 'home.html', {'latest_article': latest_article})

def about_company(request):
    user_id = request.user.id
    info = CompanyInfo.objects.first()
    return render(request, 'about.html', {'company_info': info, 'user_id': user_id})

def news(request):
    news = Article.objects.all().order_by('date')
    return render(request, 'news.html', {'news': news})

def department_list(request):
    departments = Department.objects.all()
    return render(request, 'departments.html', {'departments': departments})

def insurance_type_list(request):
    insurance_types = InsuranceType.objects.all()
    return render(request, 'insurance_types.html', {'insurance_types': insurance_types})

def promo_list(request):
    promos = Promo.objects.filter(expiry_date__gte=datetime.now())
    return render(request, 'promos.html', {'promos': promos})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user is not None:
                login(request, user)
                logger.info(f'User {username} successfully logged in after registration.')
                return redirect('home')
            else:
                logger.error(f'Authentication failed for user {username} after registration.')
                return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f'User {user.username} successfully logged in.')
            return redirect('home')
        else:
            logger.error('Authentication form invalid: %s', form.errors)
            print(form.errors)  # Вывод ошибок для отладки
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def faqs(request):
    faqs = FAQ.objects.all()
    return render(request, 'faqs.html', {'faqs': faqs})

def vacancies(request):
    vacancies = Vacancy.objects.all()
    return render(request, 'vacancies.html', {'vacancies': vacancies})

def reviews(request):
    reviews = Review.objects.all()
    return render(request, 'reviews.html', {'reviews': reviews})

class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(label='Assessment', min_value=1, max_value=5)
    class Meta:
        model = Review
        fields = ['name', 'rating','text']
        labels = {
            'name': 'Topic',
            'rating': 'Assessment',
            'text': 'Text',
        }

class ReviewCreateView(View):
    def get(self, request, **kwargs):
        if request.user.is_authenticated and request.user.status == 'customer':
            
            logging.info(f"{request.user.username} called ReviewCreateView (status: {request.user.status} | user's Timezone: {request.user.timezone})")

            form = ReviewForm()
            is_agent = request.user.status == 'agent'

            return render(request, 'review_create_form.html', {'form': form, 'is_agent': is_agent})
        return redirect('login')

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.status == 'customer':
            form = ReviewForm(request.POST)
            if form.is_valid():
                logging.info(f"ReviewForm has no errors)")

                name = form.cleaned_data['name']
                rating = form.cleaned_data['rating']
                text = form.cleaned_data['text']

                review = Review.objects.create(name=name, rating=rating, text=text, user=request.user)
                logging.info(f"Review '{review.name}' was created by {request.user.username} ")
                return redirect('reviews')
        logging.warning("User is not authenticated")
        return redirect('login')

class ReviewEditView(View):
    def get(self, request, review_id, *args, **kwargs):
        review = get_object_or_404(Review, id=review_id)
        if request.user.is_authenticated and review.user == request.user:
            form = ReviewForm(instance=review)
            return render(request, 'review_edit.html', {'form': form, 'review': review})
        return redirect('login')

    def post(self, request, review_id, *args, **kwargs):
        review = get_object_or_404(Review, id=review_id)
        if request.user.is_authenticated and review.user == request.user:
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save()
                return redirect('reviews')
        return render(request, 'review_edit.html', {'form': form, 'review': review})

class ReviewDeleteView(View):
    def get(self, request, review_id, *args, **kwargs):
        review = get_object_or_404(Review, id=review_id)
        if request.user.is_authenticated and review.user == request.user:
            review.delete()
        return redirect('reviews')


def privacy_policy(request):
    return render(request, 'privacy.html')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def contract_list(request):
    contracts = Contract.objects.filter(client=request.user)
    return render(request, 'contracts.html', {'contracts': contracts})

@login_required
def new_contract(request):
    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            contract = form.save(commit=False)
            contract.client = request.user
            promo_code = form.cleaned_data.get('promo_code')
            if promo_code:
                try:
                    promo = Promo.objects.get(code=promo_code)
                    contract.promo_code = promo_code  # Сохраняем промокод в контракте
                except Promo.DoesNotExist:
                    pass  # Промокод не существует, игнорируем
                
            contract.save()

            return redirect('contract_list')
    else:
        form = ContractForm()
    return render(request, 'new_contract.html', {'form': form})

@login_required
def edit_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    if contract.client != request.user or contract.is_processed:
        return HttpResponseForbidden("You are not allowed to edit this contract.")

    if request.method == 'POST':
        form = ContractForm(request.POST, instance=contract)
        if form.is_valid():
            contract = form.save(commit=False)
            promo_code = form.cleaned_data.get('promo_code')
            if promo_code:
                try:
                    promo = Promo.objects.get(code=promo_code)
                    contract.promo_code = promo_code  # Сохраняем промокод в контракте
                except Promo.DoesNotExist:
                    pass
            contract.save()
            return redirect('contract_list')
    else:
        form = ContractForm(instance=contract)
    return render(request, 'edit_contract.html', {'form': form, 'contract': contract})

@login_required
def delete_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    if contract.client != request.user or contract.is_processed:
        return HttpResponseForbidden("You are not allowed to delete this contract.")

    if request.method == 'POST':
        contract.delete()
        return redirect('contract_list')
    return render(request, 'confirm_delete.html', {'contract': contract})

@login_required
def new_policy(request):
    if request.method == 'POST':
        form = InsurancePolicyForm(request.POST)
        if form.is_valid():
            insurance_policy = form.save(commit=False)  # Создаем экземпляр InsurancePolicy, но не сохраняем его в базу данных пока

            if insurance_policy.start_date >= insurance_policy.end_date:
                # Валидация дат
                logger.exception("ValidationError: Start date must be before end date")
                raise ValidationError("Start date must be before end date")
            
            # Сохраняем InsurancePolicy в базу данных
            insurance_policy.save()

            # Помечаем контракт как обработанный
            contract = insurance_policy.contract
            if contract:
                contract.is_processed = True
                contract.save()

            return redirect('policy_list')
        
    else:
        form = InsurancePolicyForm()
    return render(request, 'new_policy.html', {'form': form})

@login_required
def policy_list(request):
    policies = InsurancePolicy.objects.filter(agent=request.user)
    is_agent = request.user.status == 'agent'
    return render(request, 'policy_list.html', {'policies': policies, 'is_agent': is_agent})

@login_required
def agent_list(request):
    agents = User.objects.filter(status='agent')
    return render(request, 'contacts.html', {'agents': agents})

@login_required
def agent_salary_list(request):
    salaries = AgentSalary.objects.all()
    return render(request, 'agent_salaries.html', {'salaries': salaries})

@login_required
def search_contracts(request):
    if request.method == 'POST':
        form = ContractSearchForm(request.POST)
        if form.is_valid():
            client_name = form.cleaned_data.get('client')
            contracts = Contract.objects.all()
            if client_name:
                contracts = contracts.filter(client__username__icontains=client_name)
            return render(request, 'contract_search_results.html', {'contracts': contracts})
    else:
        form = ContractSearchForm()
    return render(request, 'contract_search.html', {'form': form})



def get_dog_breeds():
    url = 'https://dog.ceo/api/breeds/list/all'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        breeds = data.get('message', {}).keys()
        return breeds
    else:
        print(f'Ошибка: {response.status_code}')
        return []

@login_required
def dog_breeds(request):
    breeds = get_dog_breeds()
    return render(request, 'dog_breeds.html', {'breeds': breeds})

def get_random_joke():
    url = 'https://official-joke-api.appspot.com/jokes/random'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        joke = data.get('setup') + ' ' + data.get('punchline')
        return joke
    else:
        print(f'Ошибка: {response.status_code}')
        return 'Не удалось получить шутку'

@login_required
def joke(request):
    joke = get_random_joke()
    return render(request, 'joke.html', {'joke': joke})


def visualize_clients_employees(request):
    # Получение количества клиентов и сотрудников из базы данных
    agents_count = User.objects.filter(status='agent').count()
    customers_count = User.objects.filter(status='customer').count()

    # Данные для визуализации
    categories = ['Клиенты', 'Сотрудники']
    counts = [customers_count, agents_count]

    # Создание круговой диаграммы
    plt.figure(figsize=(8, 6))
    plt.pie(counts, labels=categories, autopct='%1.1f%%', colors=['skyblue', 'lightgreen'], startangle=90)
    plt.title('Соотношение клиентов и сотрудников в компании')
    plt.axis('equal')  # Чтобы сделать круговую диаграмму круглой

    # Сохранение диаграммы в виде изображения
    image_path = os.path.join(settings.MEDIA_ROOT, 'images', 'client_employee_pie_chart.png')
    plt.savefig(image_path)

    # Передача пути к изображению в контекст шаблона для отображения на веб-странице
    context = {'image_path': os.path.join(settings.MEDIA_URL, 'images', 'client_employee_pie_chart.png')}
    return render(request, 'visualization.html', context)

def calculate_statistics(request):
    # Средний возраст клиентов
    average_age = User.objects.filter(status='customer').aggregate(Avg('age'))['age__avg']

    # Медианный возраст клиентов
    ages = list(User.objects.filter(status='customer').values_list('age', flat=True))
    median_age = np.median(ages) if ages else None

    # Количество активных и завершенных страховых полисов
    active_policies_count = InsurancePolicy.objects.filter(is_active=True).count()
    completed_policies_count = InsurancePolicy.objects.filter(is_active=False).count()

    # Среднее количество страховых полисов на агента
    agent_policies = InsurancePolicy.objects.values('agent').annotate(count=Count('policy_number'))
    avg_policies_per_agent = np.mean([agent['count'] for agent in agent_policies]) if agent_policies else 0

    context = {
        'average_age': average_age,
        'median_age': median_age,
        'active_policies_count': active_policies_count,
        'completed_policies_count': completed_policies_count,
        'avg_policies_per_agent': avg_policies_per_agent,
    }

    return render(request, 'statistics.html', context)