from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("<h4>hello world.. ооо винки пивет</h4>")

def about(request):
    return HttpResponse("Данный проект будет посвящен помощи в расчетах для игры Genshin Impact")
