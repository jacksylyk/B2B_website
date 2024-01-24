from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from users.models import Company, BusinessType

User = get_user_model()


@admin.register(User)
class UserAdmin(UserAdmin, admin.ModelAdmin):
    ordering = ['id']
    list_display = ['email', 'first_name', 'last_name', 'phone', 'company_info']
    search_fields = ['email', 'first_name', 'last_name', 'phone']

    def company_info(self, obj):
        if obj.company:
            return f"{obj.company.legal_company_name} - {obj.company.field_of_activity}"
        return None

    company_info.short_description = 'Company Information'

    fieldsets = [
        (_('Персональные данные'), {
            'fields': [
                'email',
                'password',
                'first_name',
                'last_name',
                'phone',
            ],
        }),
        (_('Permissions'), {
            'fields': [
                'is_active',
                'is_staff',
                'is_superuser',
            ]
        }),
        (_('Important dates'), {
            'fields': [
                'last_login',
            ]
        })

    ]

    add_fieldsets = (
        (None,
         {
             'classes': ('wide',),
             'fields': [
                 'first_name',
                 'last_name',
                 'phone',
                 'email',
                 'password1',
                 'password2',
                 'is_active',
                 'is_staff',
                 'is_superuser',
             ]
         }

         )
    )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = [
        'legal_company_name',
        'field_of_activity',
        'legal_company_address'
    ]
    search_fields = [
        'legal_company_name',
    ]


@admin.register(BusinessType)
class BusinessTypeAdmin(admin.ModelAdmin):
    list_display = [
        'business_name',
        'description',
    ]
