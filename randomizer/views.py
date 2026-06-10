from django.shortcuts import render

def index(request):
    return render(request, 'randomizer/index.html', {'room_code': ''})

def room(request, room_code):
    return render(request, 'randomizer/index.html', {'room_code': room_code.upper()})
