from django.core.exceptions import ValidationError
from django.urls import reverse
from django.db import models
from django.test import TestCase, Client
import json

from .models import Continent, Country


class BasicDataTestCase(TestCase):
    fixtures = ['countrydata.xml']

    def testGettingContinent(self):
        europe = Continent.objects.get(code="eu")
        self.assertEqual(europe.name, "Europe", "Getting continent Europe")

    def testCreatingContinent(self):
        Continent.objects.create(name="Testcontinent", code="tc")
        testcontinent = Continent.objects.get(code="tc")
        self.assertEqual(testcontinent.name, "Testcontinent", "Getting a just created continent")

    def _testfieldtype(self, model, modelname, fieldname, type):
        try:
          field = model._meta.get_field(fieldname)
          self.assertTrue(isinstance(field, type), "Testing the type of %s field in model %s"%(fieldname, modelname))
        except FieldDoesNotExist:
          self.assertTrue(False, "Testing if field %s exists in model %s"%(fieldname, modelname))
        return field

    def testFieldTypes(self):
      self._testfieldtype(Continent, 'Continent', 'name', models.CharField)
      self._testfieldtype(Continent, 'Continent', 'code', models.CharField)
      self._testfieldtype(Country, 'Country', 'code', models.CharField)
      self._testfieldtype(Country, 'Country', 'name', models.CharField)
      self._testfieldtype(Country, 'Country', 'capital', models.CharField)
      self._testfieldtype(Country, 'Country', 'population', models.PositiveIntegerField)
      self._testfieldtype(Country, 'Country', 'area', models.PositiveIntegerField)
      self._testfieldtype(Country, 'Country', 'code', models.CharField)

    def testModelOrdering(self):
        prev = None

        # Check both Continent and Country classes
        for ModelClass in (Continent, Country):

            # Iterate over all objects and check that the next is greater than the previous
            for cur in ModelClass.objects.all():
                if prev:
                    self.assertTrue(prev.name < cur.name, "Checking ordering of objects in " + cur.__class__.__name__ + ". Did you remember to set the default ordering?")
                prev = cur
            prev = None

    def testCountryCreationValidation(self):
        europe = Continent.objects.get(code="eu")

        code_conflict = Country(name="Example",
                                 population=100,
                                 area=1000,
                                 capital="capital",
                                 code="fi",
                                 continent=europe)

        valid_country = Country(name="Example",
                                 population=100,
                                 area=1000,
                                 capital="capital",
                                 code="xx",
                                 continent=europe)

        # Cleaning conflicting code should raise an error
        self.assertRaises(ValidationError, code_conflict.full_clean, "Code for Country should be unique")

        # This should not raise any errors
        try:
          valid_country.full_clean()
        except:
          self.assertTrue(False, "Saving a country with valid data failed")

    def testCountryThroughContinent(self):

        # Get continent
        europe = Continent.objects.get(code="eu")

        # Test that foreign key relation works backwards
        try:
          fi = europe.countries.get(code="fi")
        except:
          self.assertTrue(False, "Getting country failed. Did you remember that countries should be accessed through attribute countries?")
        self.assertEqual(fi.name, "Finland", "Getting a country from a continent")

    def testCountryIsRelatedManager(self):
        continent = Continent.objects.first()
        self.assertEqual(type(continent.countries).__name__, 'RelatedManager', 'Use ForeignKey related_name to set the backwards relation.')


class JsonTestCase(TestCase):
    fixtures = ['countrydata.xml']

    def setUp(self):
        """ Initializes the Django test client before each test """
        self.client = Client()

    def _url(self, continent_code, country_code=None):
        if not country_code:
            return reverse('continent-json', args=[continent_code])
        return reverse('country-json', args=[continent_code, country_code])

    def testJsonContinents(self):
        for continent in Continent.objects.all():
            response = self.client.get(self._url(continent.code))
            self.assertEquals(response.status_code, 200, "Testing JSON continent request status code.")
            country_dict = json.loads(response._container[0].decode(encoding="utf-8"))

            # Check that each country name can be found under the corresponding code in dict
            for country in continent.countries.all():
                self.assertEquals(country.name, country_dict[country.code])

    def testJsonCountries(self):
        for country in Country.objects.all():
            response = self.client.get(self._url(country.continent.code, country.code))
            self.assertEquals(response.status_code, 200, "Testing JSON country request status code.")

            fields = json.loads(response._container[0].decode(encoding="utf-8"))

            # Check that each field can be found in fields dict
            self.assertEquals(country.population, fields["population"])
            self.assertEquals(country.area, fields["area"])
            self.assertEquals(country.capital, fields["capital"])

    def testJsonCallback(self):
        response = self.client.get(self._url('eu', 'no'), {"callback": "custom_callback"})
        self.assertContains(response, "custom_callback(")
        response = self.client.get(self._url('eu'), {"callback": "trigger"})
        self.assertContains(response, "trigger(")

    def testInvalidParameters(self):

        # Norway should not be found under North America
        response = self.client.get(self._url('na', 'no'))
        self.assertEquals(response.status_code, 404, "Looking for a real country in a wrong continent.")

        # There is no country "xx" in North America
        response = self.client.get(self._url('na', 'xx'))
        self.assertEquals(response.status_code, 404, "Looking for a non existent country in a real continent.")

        # There is no continent with a "xx" code
        response = self.client.get(self._url('xx', 'fi'))
        self.assertEquals(response.status_code, 404, "Looking for a real country in a non existent continent.")

        # Norway should be found under Europe
        response = self.client.get(self._url('eu', 'no'))
        self.assertEquals(response.status_code, 200, "Testing valid request status code.")
