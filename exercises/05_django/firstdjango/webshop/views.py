from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from webshop.models import Product

def starting_instructions(request):
    return render(request, "webshop/instructions.html", {})

def about(request):
    return HttpResponse("about page")

def productview(request, product_id):
    """
    Write your view implementations for exercise 4 here.
    Remove the current return line below.
    """
    template = 'webshop/product_view.html'
    try:
        p = Product.objects.get(pk=product_id)
        context = {'product' : p,}
    except Product.DoesNotExist:
        return HttpResponseNotFound("Product %s not found"%product_id)

    return render(request, template, context)

def available_products(request):
    """
    Write your view implementations for exercise 4 here.
    Remove the current return line below.
    """
    list = Product.objects.all().filter(quantity__gt=0)
    template = 'webshop/product_list.html'
    context = {'products' : list,}

    return render(request, template, context)
