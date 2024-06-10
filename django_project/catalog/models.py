from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from tzlocal import get_localzone_name
from decimal import Decimal
from django.utils import timezone
from datetime import datetime, timedelta
import django.forms
import re
import logging

logger = logging.getLogger(__name__)


class Article(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to='images/')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CompanyInfo(models.Model):
    text = models.TextField()
    #logo = models.ImageField(upload_to='images/')

class Term(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.question

# Филиалы компании
class Department(models.Model):

    def validate_phone(value):
        phone_pattern = re.compile(r'\+375\((29|33|44|25)\)\d{7}')
        if not re.fullmatch(phone_pattern, str(value)):
            raise django.forms.ValidationError("Неправильный номер телефона. Верный формат: +375(XX)XXXXXXX.")
        
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, validators=[validate_phone])

    def __str__(self):
        return self.name

# Пользователи системы
class User(AbstractUser):
    STATUS_CHOICES = (
        ("agent", "Agent"),
        ("customer", "Customer"),
    )

    def validate_phone(value):
        phone_pattern = re.compile(r'\+375\((29|33|44|25)\)\d{7}')
        if not re.fullmatch(phone_pattern, str(value)):
            raise django.forms.ValidationError("Неправильный номер телефона. Верный формат: +375(XX)XXXXXXX.")
        
    def validate_age(value):
        if value < 18 or value > 100:
            raise django.forms.ValidationError("Ваш возраст должен быть не меньше 18")

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="customer")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, validators=[validate_phone])
    age = models.PositiveSmallIntegerField(default=18, validators=[validate_age])
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL)
    timezone = get_localzone_name()


    groups = models.ManyToManyField(
        'auth.Group',
        related_name='catalog_user_set',  # Custom related name
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='catalog_user_set',  # Custom related name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return f"{self.username}"

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    date = models.DateField(auto_now_add=True)

class Contact(models.Model):
    description = models.TextField()
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'status': 'agent'})
    photo = models.ImageField(upload_to='images/')

class Vacancy(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField()
    need = models.TextField()

class Review(models.Model):
    name = models.CharField(max_length=100)
    rating = models.IntegerField()
    text = models.TextField()
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, related_name="reviews", on_delete=models.CASCADE)

# Виды страхования
class InsuranceType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    commission_rate = models.FloatField()  # Процентная ставка для расчета зарплаты агентов
    tariff_rate = models.FloatField(default=0)  # Тарифная ставка

    def __str__(self):
        return self.name

# Объекты страхования
class InsurableObject(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField()

    def __str__(self):
        return f"{self.name}: {self.description}"

class InsuranceRisk(models.Model):
    insurance_type = models.ForeignKey(InsuranceType, on_delete=models.CASCADE, related_name='risks', default='')
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return f"{self.name} risk"


# Промокоды
class Promo(models.Model):
    code = models.CharField(max_length=10)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    expiry_date = models.DateField(default=datetime.now() + timedelta(days=1))

# Использование промокодов
class PromoUsage(models.Model):
    promo = models.ForeignKey(Promo, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

# Заказы клиентов
class Contract(models.Model):
    client = models.ForeignKey(User, related_name='client_contracts', on_delete=models.CASCADE, limit_choices_to={'status': 'customer'})
    department = models.ForeignKey(Department, related_name='contracts', on_delete=models.CASCADE)
    insurance_type = models.ForeignKey(InsuranceType, related_name='contracts', on_delete=models.CASCADE)
    insurable_object = models.ForeignKey(InsurableObject, related_name='contracts', on_delete=models.CASCADE)
    insurance_risk = models.ForeignKey(InsuranceRisk, related_name='contracts', on_delete=models.CASCADE, default='')
    insurance_amount = models.FloatField()  # Страховая сумма
    created_at = models.DateTimeField(auto_now_add=True)
    promo_code = models.CharField(max_length=8, null=True)
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return f"Contract {self.id} by {self.client.username}"
    
    def calculate_final_amount(self):
        final_amount = Decimal(str(self.insurance_amount)) + Decimal(str(self.insurance_type.tariff_rate))
        if self.promo_code:
            try:
                promo = Promo.objects.get(code=self.promo_code)
                current_date = timezone.now().date()
                if promo.expiry_date > current_date:
                    final_amount -= Decimal(str(promo.discount))
            except Promo.DoesNotExist:
                pass  # Promo code doesn't exist, do nothing
        return final_amount

# Договоры страхования
class InsurancePolicy(models.Model):
    policy_number = models.AutoField(primary_key=True) # Номер страхового счета
    agent = models.ForeignKey(User, related_name='agent_policies', on_delete=models.CASCADE, limit_choices_to={'status': 'agent'})
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    contract = models.ForeignKey(Contract, on_delete=models.DO_NOTHING, default='')

    def __str__(self):
        return f"Policy {self.policy_number}"

    def save(self, *args, **kwargs):
        if self.start_date >= self.end_date:
            logger.exception("ValidationError: Start date must be before end date")
            raise ValidationError("Start date must be before end date")
        super().save(*args, **kwargs)

    def calculate_agent_salary(self):
        return self.contract.insurance_amount * self.contract.insurance_type.tariff_rate * self.contract.insurance_type.commission_rate / 100

# Модель для расчета зарплаты агента
class AgentSalary(models.Model):
    agent = models.ForeignKey(User, related_name='salaries', on_delete=models.CASCADE, limit_choices_to={'status': 'employee'})
    policy = models.ForeignKey(InsurancePolicy, related_name='salaries', on_delete=models.CASCADE)
    commission_amount = models.FloatField()

    def __str__(self):
        return f"Salary for {self.agent} on policy {self.policy.policy_number}"

    def calculate_commission(self):
        self.commission_amount = self.policy.calculate_insurance_payment() * (self.policy.insurance_type.commission_rate / 100)
        self.save()

    def save(self, *args, **kwargs):
        self.calculate_commission()
        super().save(*args, **kwargs)


