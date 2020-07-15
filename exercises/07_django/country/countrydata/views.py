from django.http import Http404, HttpResponse
import json

from .models import Continent, Country


def continent_json(request, continent_code):

    try:
        cont = Continent.objects.get(code=continent_code)
    except Continent.DoesNotExist:
        raise Http404("Continent requested NOT FOUND")

    countries = cont.countries.all()
    countries_json = {}
    for c in countries:
        countries_json[c.code] = c.name

    res = json.dumps(countries_json)

    req_str = request.META['QUERY_STRING']

    if 'callback' in req_str:
        func_name = req_str.split('=')[1] # or request.GET['callback']
        json_body = res

        res = func_name+'('+str(country_json)+')'
        return HttpResponse(res, content_type="application/javascript")

    return HttpResponse(res, content_type="application/json")



def country_json(request, continent_code, country_code):

    try:
        cont = Continent.objects.get(code=continent_code)
    except Continent.DoesNotExist:
        raise Http404("Continent requested NOT FOUND")
    try:
        c = Country.objects.get(code=country_code, continent=cont)
    except Country.DoesNotExist:
        raise Http404("Country requested NOT FOUND")

    country_json = {
                        "area": c.area,
                        "population": c.population,
                        "capital": c.capital
                    }
    res = json.dumps(country_json)

    str = request.META['QUERY_STRING']

    if 'callback' in str:
        func_name = str.split('=')[1] # or request.GET['callback']
        json_body = res

        res = func_name+'('+json_body+')'
        return HttpResponse(res, content_type="application/javascript")

    return HttpResponse(res, content_type="application/json")
