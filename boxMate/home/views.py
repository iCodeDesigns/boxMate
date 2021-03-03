from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.db.models import Count
from django.views.decorators.cache import never_cache
from django.shortcuts import render, reverse, redirect

from taxManagement.models import Submission, InvoiceHeader
from taxManagement.java import call_java
from home.forms import CustomUserCreationForm


def register(request):
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_staff = True
            user.is_active = True
            user.save()
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('home:user-login'))
            else:

                messages.error(request, 'This account is deactivated!')
                return render(request, 'login.html')
        else:
            print(form.errors)
    return render(request, 'register.html', {'register_form': form})


@never_cache
def user_login(request):
    next = request.GET.get('next')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if next:
                    return redirect(next)
            else:
                messages.error(request, 'Inactive Account')

            if user.issuer is not None: 
                return redirect(reverse('home:homepage'))
            else:
                return redirect('issuer:create-issuer')
        else:
            messages.error(request, ('Login Failed, Please Check the Username or Password'))
    return render(request, 'login.html')


@login_required(login_url='home:user-login')
def home_page(request):
    total_invoice_count = InvoiceHeader.objects.all().count()
    total_submited_invoice = Submission.objects.values('invoice').annotate(total=Count('invoice'))
    total_submited_invoice_count = 0

    for invoice in total_submited_invoice:
        total_submited_invoice_count += invoice['total']
    total_not_submited_invoice_count = total_invoice_count-total_submited_invoice_count

    #jar = call_java.java_func("test" ,"Dreem", "08268939")
    dashboard_context = {
        "total_invoice_count":total_invoice_count,
        "total_submited_invoice_count":total_submited_invoice_count,
        "total_not_submited_invoice_count":total_not_submited_invoice_count,
      #  "jar":jar
    }
    return render(request, 'index.html', dashboard_context)


@login_required(login_url='home:user-login')
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home:user-login'))
