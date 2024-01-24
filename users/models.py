from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from .manager import Manager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        _('email address'),
        unique=True,
    )
    first_name = models.CharField(max_length=128, verbose_name='Имя')
    last_name = models.CharField(max_length=128, verbose_name='Фамилия')
    phone = models.CharField(max_length=20, verbose_name='Личный телефон', unique=True)
    is_staff = models.BooleanField(default=False, verbose_name='Доступ к админ панели')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = Manager()

    class Meta:
        verbose_name_plural = 'Пользователи'


class Company(models.Model):
    legal_company_name = models.CharField(max_length=256, verbose_name='Юридическое наименование')
    field_of_activity = models.CharField(max_length=128, verbose_name='Сфера деятельности')
    type_of_business = models.ForeignKey('BusinessType', on_delete=models.CASCADE, verbose_name='Тип бизнеса',
                                         related_name='company_types')
    bin_number = models.CharField(max_length=12, verbose_name="БИН")
    bik_number = models.CharField(max_length=10, verbose_name="БИК")
    bank_name = models.CharField(max_length=128, verbose_name="Банк")
    iban_number = models.CharField(max_length=34, verbose_name="ИИК (номер счёта)")
    legal_company_address = models.CharField(max_length=256, verbose_name="Юридический адрес ")
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="company",
        verbose_name="Пользователь"
    )

    class Meta:
        verbose_name_plural = 'Данные компании'


class BusinessType(models.Model):
    business_name = models.CharField(max_length=255, verbose_name="Бизнес")
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return self.business_name

    class Meta:
        verbose_name_plural = 'Типы бизнеса'
