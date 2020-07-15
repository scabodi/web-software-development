from django.test import TestCase, Client
from django.urls import reverse
from django.template.loader import render_to_string

from countrydata.models import Continent, Country


class TemplateTestCase(TestCase):
    fixtures = ['countrydata.xml']

    def setUp(self):
        self.client = Client()

    def _url(self, continent_code=None):
        if not continent_code:
            return reverse('continent-all')
        return reverse('continent-details', args=[continent_code])

    def testInvalidUrl(self):
        response = self.client.get(self._url('xx'))
        self.assertEquals(response.status_code, 404, "Requesting a page with an invalid country code.")

    def testPageContents(self):
        """ This test requests pages for all continents and checks that all relevant data of
        their countries can be found on the page. """
        for continent in Continent.objects.all():
            response = self.client.get(self._url(continent.code), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEquals(response.status_code, 200, "Testing request status code.")
            for country in Country.objects.all():
                if country.continent == continent:
                    self.assertContains(response, country.name)
                    self.assertContains(response, country.capital)
                    self.assertContains(response, country.population)
                    self.assertContains(response, country.area)
                else:
                    # Parts of some countries names are found in two different continents
                    if country.name in ("Georgia", "France", "Netherlands", "Spain", "Guinea", "Antarctica"):
                        continue
                    self.assertNotContains(response, country.name)

    def testContinentMenu(self):
        """ Tests that the continent menu is rendered correctly """
        all_continents = ({'code': 'qq', 'name': 'Quu'},
                          {'code': 'ww', 'name': 'Wee'})
        ren = render_to_string("selectui/continentmenu.html", {'all_continents': all_continents})
        for continent in all_continents:
            self.assertTrue(ren.find(self._url(continent['code'])) > -1,
                "Testing if the rendered menu contains correct URL for continent")
            self.assertTrue(ren.find(continent['name']) > -1,
                "Testing if the rendered menu contains correct continent name")

    def testPartialContents(self):
        """ Tests that the response is different when requesting a page with an Ajax request. """
        for continent in Continent.objects.all():
            url = self._url(continent.code)

            # Test with an Ajax request
            response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEquals(response.status_code, 200, "Testing request status code.")
            self.assertNotContains(response, "<html>")
            self.assertNotContains(response, "<body>")
            self.assertEquals(response.status_code, 200, "Testing request status code.")
            self.assertTemplateUsed(response, "selectui/countrytable.html", "Testing that the right template was rendered")
            self.assertTemplateNotUsed(response, "selectui/index.html", "Testing that index.html was not rendered on Ajax request")
            self.assertTemplateNotUsed(response, "selectui/continentmenu.html", "Testing that continentmenu.html was not rendered on Ajax request")

            for country in Country.objects.all():
                if country.continent == continent:
                    self.assertContains(response, country.name)
                    self.assertContains(response, country.capital)
                    self.assertContains(response, country.population)
                    self.assertContains(response, country.area)
                else:
                    # Parts of some countries names are found in two different continents
                    if country.name in ("Georgia", "France", "Netherlands", "Spain", "Guinea", "Antarctica"):
                        continue
                    self.assertNotContains(response, country.name)

            # Test with a non-Ajax request
            response = self.client.get(url)
            self.assertEquals(response.status_code, 200, "Testing request status code.")
            self.assertContains(response, "<html>")
            self.assertContains(response, "<body>")
