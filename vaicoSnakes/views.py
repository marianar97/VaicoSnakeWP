from django.shortcuts import render

# Create your views here.
#from django.http import HttpResponse

def home(request):
    return render(request, 'basic/index.html')

def contact(request):
    return render(request, 'basic/contact.html')

def services(request):
    return render(request, 'basic/services.html')
