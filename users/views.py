from django.contrib.auth import authenticate, login, get_user_model, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View, generic

from users.forms import UserCreationForm, CompanyCreationForm
from users.models import Company


class Register(View):
    template_name = 'registration/register.html'

    def get(self, request):
        # Retrieve form data from session if available
        form_data = request.session.pop('registration_form_data', None)
        if form_data:
            # If form data is available, use it to initialize the form
            form = UserCreationForm(data=form_data)
        else:
            # Otherwise, create a new form
            form = UserCreationForm()

        context = {'form': form}
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

        # Save the form data in the session
        request.session['registration_form_data'] = request.POST

        context = {'form': form}
        return render(request, self.template_name, context)


class CompanyRegister(generic.CreateView):
    template_name = "registration/company_register.html"
    model = Company
    form_class = CompanyCreationForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('store:index')


def registration_cancel(request):
    if request.method == 'POST':
        user_id = request.user.id
        user = get_user_model().objects.get(id=user_id)

        # Logout and delete the user first
        logout(request)
        user.delete()

        # Save the form data in the session
        request.session['registration_form_data'] = request.POST

    return redirect('register')