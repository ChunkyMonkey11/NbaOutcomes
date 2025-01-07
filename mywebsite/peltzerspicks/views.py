from django.shortcuts import render
from django.http import HttpResponse

def Home(request):
    return HttpResponse('<h1>PeltzersPicks</h1>')

def about(request):
    return HttpResponse('<h1>About Page</h1>')
