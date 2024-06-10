from django.test import TestCase
from django.test import Client
from django.urls import reverse
from .models import Contract, InsuranceType
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from views import *
from django.core.exceptions import ValidationError

class RegistrationFormTest(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def test_registration_form_valid(self):
        form_data = {
            'username': 'user',
            'last_name': 'User',
            'first_name': 'User',
            'middle_name': 'User',
            'email' : 'test@gmail.com',
            'phone_number': '+375(29)1262368',
            'address': 'Test',
            'age': 30,
            'department' : 'Test',
            'password1': 'testpassword111',
            'password2': 'testpassword111',
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_registration_form_invalid_password_mismatch(self):
        form_data = {
            'username': 'user',
            'last_name': 'User',
            'first_name': 'User',
            'middle_name': 'User',
            'email' : 'test@gmail.com',
            'phone_number': '+375(29)1262368',
            'address': 'Test',
            'age': 30,
            'department' : 'Test',
            'password1': 'testpassword111',
            'password2': 'testpassword112',
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password2'], ['The two password fields didn’t match.'])

    def test_post_invalid_age(self):
        client = Client()
        data = {
            'username': 'user',
            'last_name': 'User',
            'first_name': 'User',
            'middle_name': 'User',
            'email' : 'test@gmail.com',
            'phone_number': '+375(29)1262368',
            'address': 'Test',
            'age': 10,
            'department' : 'Test',
            'password1': 'testpassword111',
            'password2': 'testpassword112',
        }
        with self.assertRaises(ValidationError):
            client.post(reverse('register'), data)
        self.assertFalse(User.objects.filter(username='user').exists())

    def test_post_invalid_phone(self):
        client = Client()
        data = {
            'username': 'user',
            'last_name': 'User',
            'first_name': 'User',
            'middle_name': 'User',
            'email' : 'test@gmail.com',
            'phone_number': '+375291262368',
            'address': 'Test',
            'age': 30,
            'department' : 'Test',
            'password1': 'testpassword111',
            'password2': 'testpassword112',
        }
        with self.assertRaises(ValidationError):
            client.post(reverse('register'), data)
        self.assertFalse(User.objects.filter(username='user').exists())

class DepartmentModelTest(TestCase):
    def test_department_model(self):
        department = Department.objects.create(name='Test Department', address='Test Address', phone='+375(29)1234567')
        self.assertEqual(department.name, 'Test Department')
        self.assertEqual(department.address, 'Test Address')
        self.assertEqual(department.phone, '+375(29)1234567')

class ContractModelTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name='Test Department', address='Test Address', phone='+375(29)1234567')
        self.user = User.objects.create_user(username='test_user', first_name='Test', last_name='User', email='test@example.com', phone_number='+375(29)1234567', address='Test Address', age=25, department=self.department, password='testpassword')
        self.insurance_type = InsuranceType.objects.create(name='Test Type', description='Test Description', commission_rate=0.1)

    def test_contract_model(self):
        contract = Contract.objects.create(client=self.user, department=self.department, insurance_type=self.insurance_type, insurance_amount=1000)
        self.assertEqual(contract.client, self.user)
        self.assertEqual(contract.department, self.department)
        self.assertEqual(contract.insurance_type, self.insurance_type)
        self.assertEqual(contract.insurance_amount, 1000)

class InsurancePolicyModelTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name='Test Department', address='Test Address', phone='+375(29)1234567')
        self.agent = User.objects.create_user(username='agent', first_name='Agent', last_name='Smith', email='agent@example.com', phone_number='+375(29)1234568', address='Agent Address', age=30, department=self.department, status='agent', password='testpassword')
        self.contract = Contract.objects.create(client=self.agent, department=self.department, insurance_type=InsuranceType.objects.create(name='Test Type', description='Test Description', commission_rate=0.1), insurance_amount=1000)

    def test_insurance_policy_model(self):
        policy = InsurancePolicy.objects.create(agent=self.agent, start_date=datetime.now(), end_date=datetime.now() + timedelta(days=365), contract=self.contract)
        self.assertEqual(policy.agent, self.agent)
        self.assertEqual(policy.start_date.date(), datetime.now().date())
        self.assertEqual(policy.end_date.date(), (datetime.now() + timedelta(days=365)).date())
        self.assertTrue(policy.is_active)
        self.assertEqual(policy.contract, self.contract)

class PromoModelTest(TestCase):
    def test_promo_model(self):
        expiry_date = datetime.now() + timedelta(days=1)
        promo = Promo.objects.create(code='TEST123', discount=10, expiry_date=expiry_date)
        self.assertEqual(promo.code, 'TEST123')
        self.assertEqual(promo.discount, 10)
        self.assertEqual(promo.expiry_date.date(), expiry_date.date())

