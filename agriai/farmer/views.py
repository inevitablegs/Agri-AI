# agriai/farmer/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext as _
from django.http import JsonResponse

def home(request):
    context = {
        'welcome_message': _("Welcome to Agri-AI Assistant"),
        'features': [
            _("Multilingual support"),
            _("Crop recommendations"),
            _("Weather information"),
            _("Market prices")
        ]
    }
    return render(request, 'farmer/home.html', context)

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'farmer/signup.html', {
        'form': form,
        'signup_title': _("Create your farmer account")
    })

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    
    return render(request, 'farmer/login.html', {
        'form': form,
        'login_title': _("Farmer Login")
    })

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    greeting = _("Welcome, %(username)s!") % {'username': request.user.username}
    
    context = {
        'greeting': greeting,
        'quick_actions': [
            {'title': _("Check Weather"), 'icon': 'cloud'},
            {'title': _("Crop Advice"), 'icon': 'leaf'},
            {'title': _("Market Prices"), 'icon': 'graph-up'}
        ]
    }
    return render(request, 'farmer/dashboard.html', context)

def get_agriculture_data(request):
    # This would connect to your agriculture data sources
    # Sample implementation with translations
    data = {
        'weather': {
            'description': _("Sunny with partial clouds"),
            'temperature': "28°C",
            'humidity': "65%"
        },
        'crop_recommendation': {
            'season': _("Rabi"),
            'crops': [_("Wheat"), _("Mustard"), _("Chickpea")]
        },
        'market_prices': {
            'wheat': "₹2100/qtl",
            'mustard': "₹4500/qtl",
            'chickpea': "₹5200/qtl"
        }
    }
    
    return JsonResponse({
        'status': 'success',
        'data': data
    })