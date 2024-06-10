from django.contrib import admin
from django import forms 
from .models import Article, FAQ, CompanyInfo, Term, Contact, Vacancy, Review, InsuranceType, InsuranceRisk, Department, User, InsurableObject, InsurancePolicy, User, Promo, PromoUsage, Contract, AgentSalary
    
admin.site.register(Article)
admin.site.register(CompanyInfo)
admin.site.register(Term)
admin.site.register(Contact)
admin.site.register(Vacancy)
admin.site.register(Review)
admin.site.register(InsuranceType)
admin.site.register(Department)
admin.site.register(User)
admin.site.register(InsurableObject)
admin.site.register(InsurancePolicy)
admin.site.register(InsuranceRisk)
admin.site.register(Promo)
admin.site.register(PromoUsage)
admin.site.register(Contract)
admin.site.register(FAQ)
admin.site.register(AgentSalary)
