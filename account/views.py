from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout


#i think i put the spotify stuff here for now
from dotenv import load_dotenv
#getting things that shouldn't be committed
load_dotenv()




def accountpage(request):
    return render (request, "account/account.html")

def register_view(request): 
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)
            return redirect('/account/login')
        
    context = {'form':form} 
    return render (request, "account/register.html", context)

def login_view(request): 
    if request.method =='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Usergname or Password is incorrect')
    return render (request, "account/login.html")

def logout_view(request):
    logout(request)
    return redirect('/account/login')
