from django.shortcuts import render, get_object_or_404
from .models import Cat  # Ensure this import is present
from django.http import HttpResponse
from django.views.generic.edit import CreateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def cat_index(request):
    print(type(Cat))  # Debug: Print the type of Cat
    print(Cat.__module__)  # Debug: Print the module where Cat is defined
    cats = Cat.objects.all()  # Line 13
    return render(request, 'cats/index.html', {'cats': cats})

def cat_detail(request, cat_id):
    cat = get_object_or_404(Cat, id=cat_id)
    return render(request, 'cats/detail.html', {'cat': cat})

class CatCreate(CreateView):
    model = Cat
    fields = '__all__'

class CatUpdate(UpdateView):
    model = Cat
    # Let's disallow the renaming of a cat by excluding the name field!
    fields = ['breed', 'description', 'age']

class CatDelete(DeleteView):
    model = Cat
    success_url = '/cats/'

cats = [
    Cat('Lolo', 'tabby', 'Kinda rude.', 3),
    Cat('Sachi', 'tortoiseshell', 'Looks like a turtle.', 0),
    Cat('Fancy', 'bombay', 'Happy fluff ball.', 4),
    Cat('Bonk', 'selkirk rex', 'Meows loudly.', 6)
]
