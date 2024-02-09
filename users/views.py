from django.contrib.auth import authenticate, login, get_user_model, logout
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View, generic

from users.forms import UserCreationForm, CompanyCreationForm, UserUpdateForm, CompanyUpdateForm
from users.models import Company, BusinessType
from django.contrib.auth.decorators import login_required


class Register(View):
    template_name = 'registration/register.html'

    def get(self, request):
        user_data = request.session.pop('user', None)
        form = UserCreationForm()
        if user_data:
            context = {
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'email': user_data['email'],
                'phone': user_data['phone']
            }
        else:
            context = {}
        return render(request, self.template_name, context)

    def post(self, request):
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=password)
            login(request, user)
            return redirect('company_register')

        context = {'form': form}
        return render(request, self.template_name, context)


def company_register_view(request):
    if request.method == 'POST':
        legal_company_name = request.POST.get('legal_company_name')
        field_of_activity = request.POST.get('field_of_activity')
        business_type = request.POST.get('business_type')
        bin_number = request.POST.get('bin_number')
        bik_number = request.POST.get('bik_number')
        bank_name = request.POST.get('bank_name')
        iban_number = request.POST.get('iban_number')
        legal_company_address = request.POST.get('legal_company_address')

        business_type = BusinessType.objects.get(business_name=business_type)
        Company.objects.create(legal_company_name=legal_company_name, field_of_activity=field_of_activity,
                               type_of_business=business_type, bin_number=bin_number, bank_name=bank_name,
                               iban_number=iban_number, bik_number=bik_number,
                               legal_company_address=legal_company_address, user=request.user)
        return redirect('registration_finish')

    context = {
        'business_types': BusinessType.objects.all(),
    }

    return render(request, 'registration/company_register.html', context)


def registration_cancel(request):
    if request.method == 'POST':
        user_id = request.user.id
        user = get_user_model().objects.get(id=user_id)

        email = user.email
        first_name = user.first_name
        last_name = user.last_name
        phone = user.phone

        logout(request)
        user.delete()

        context = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone
        }
        request.session['user'] = context
        return redirect('register')


def registration_finish(request):
    return render(request, 'registration/register_finish.html')


@login_required
def account_details(request):
    user = request.user
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('personal_account_detail')
    else:
        form = UserUpdateForm(instance=user)

    context = {'user': user, 'form': form}
    return render(request, 'registration/account_detail.html', context)


@login_required
def company_details(request):
    user = request.user
    try:
        company = Company.objects.get(user=user)
    except Company.DoesNotExist:
        company = None

    if request.method == 'POST':
        form = CompanyUpdateForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return redirect('company_detail')  # Assuming you have a view for viewing company details
    else:
        form = CompanyUpdateForm(instance=company)

    context = {'form': form}
    return render(request, 'registration/company_update.html', context)

