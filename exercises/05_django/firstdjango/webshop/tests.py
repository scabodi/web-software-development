from django.test import TestCase, Client
from django.db import models
import random, string, unittest

from webshop.models import Product

class SimpleTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.randstr = ''.join(random.sample(string.ascii_letters, 5))
        self.randint = random.randint(5,50)

    def test_about(self):
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 200, "Testing that a request to /about/ succeeded")
        self.assertEqual(response.content.decode("utf-8"), "about page", "Testing that the correct view was called for /about/")
        response = self.client.get('/%s/about/'%(self.randstr))
        self.assertEqual(response.status_code, 404, "Testing that /%s/about/ does not work"%(self.randstr))
        response = self.client.get('/about/%s/'%(self.randstr))
        self.assertEqual(response.status_code, 404, "Testing that /about/%s/ does not work"%(self.randstr))

    #@unittest.skip("Exercise 2")
    def test_product_url(self):
        i = random.randint(20,40)
        response = self.client.get('/products/%d/'%(i))
        self.assertEqual(response.status_code, 200, "Testing that a request to /products/%d/ succeeded"%(i))
        self.assertEqual(response.content.decode("utf-8"), "product %d"%(i), "Testing that the correct view (webshop.views.productview) was called")
        response = self.client.get('/products/-100/')
        self.assertEqual(response.status_code, 404, "Testing that /products/-100/ does not work")
        response = self.client.get('/products/%d/%s'%(i, self.randstr))
        self.assertEqual(response.status_code, 404, "Testing that /products/%d/%s does not work"%(i, self.randstr))
        response = self.client.get('/%s/products/%d/'%(self.randstr, i))
        self.assertEqual(response.status_code, 404, "Testing that /%s/products/%d/ does not work"%(self.randstr, i))

    #@unittest.skip("Exercise 2")
    def test_available_products_url(self):
        response = self.client.get("/products/")
        self.assertEqual(response.status_code, 200, "Testing that a request to /products/ succeeded")
        self.assertEqual(response.content.decode("utf-8"), "View not implemented!", "Testing that the correct view (webshop.views.available_products) was called")
        response = self.client.get("/products/%s"%(self.randstr))
        self.assertEqual(response.status_code, 404, "Testing that /products/%s does not work"%(self.randstr))
        response = self.client.get("/%s/products/"%(self.randstr))
        self.assertEqual(response.status_code, 404, "Testing that /%s/products/ does not work"%(self.randstr))

    def _test_field_type(self, model, modelname, fieldname, type):
        try:
            field = model._meta.get_field(fieldname)
            self.assertTrue(isinstance(field, type), "Testing the type of %s field in model %s"%(fieldname, modelname))
        except models.fields.FieldDoesNotExist as e:
            self.assertTrue(False, "Testing if field %s exists in model %s"%(fieldname, modelname))
        return field

    @unittest.skip("Exercise 3")
    def test_product_title(self):
        title = self._test_field_type(Product, 'Product', 'title', models.CharField)
        self.assertEquals(title.max_length, 255, "Testing the max_length of title field")
        self.assertTrue(title.unique, "Testing if title is set to unique")

    @unittest.skip("Exercise 3")
    def test_product_description(self):
        desc = self._test_field_type(Product, 'Product', 'description', models.TextField)

    @unittest.skip("Exercise 3")
    def test_product_image(self):
        imageurl = self._test_field_type(Product, 'Product', 'image_url', models.URLField)
        self.assertTrue(imageurl.blank, "Testing that image_url can be blank")

    @unittest.skip("Exercise 3")
    def test_product_quantity(self):
        quantity = self._test_field_type(Product, 'Product', 'quantity', models.IntegerField)
        self.assertEquals(quantity.default, 0, "Testing that quantity has default value set to 0")

    @unittest.skip("Exercise 3")
    def test_sell_method(self):
        p = Product(title='title', description='desc', quantity=self.randint)
        p.save()
        p.sell()
        p = Product.objects.get(pk=p.pk)
        self.assertEquals(p.quantity, self.randint - 1, "Testing that the quantity was decreased when calling sell")

    def _add_5_products(self):
        for i in range(5):
            p = Product()
            p.title = 'prod%d'%(i)
            p.description = 'product%d'%(i)
            p.quantity = i
            p.save()

    @unittest.skip("Exercise 4")
    def test_available_products(self):
        self._add_5_products()
        response = self.client.get('/products/')
        self.assertEquals(response.status_code, 200, "Testing that a status code 200 is returned by the view")
        self.assertTemplateUsed(response, 'webshop/product_list.html', "Testing that the correct template (webshop/product_list.html) was rendered")
        available = response.context['products']
        real = Product.objects.filter(quantity__gt=0)
        for product in available:
            self.assertTrue(product in real, "Testing that the included products are correct")

    @unittest.skip("Exercise 4")
    def test_productview(self):
        self._add_5_products()
        response = self.client.get('/products/1/')
        self.assertEquals(response.status_code, 200, "Testing that a status code 200 is returned by the view")
        self.assertTemplateUsed(response, 'webshop/product_view.html', "Testing that the correct template (webshop/product_view.html) was rendered")
        product = response.context['product']
        self.assertEquals(product, Product.objects.get(pk=1), "Testing that the correct product was rendered")

    @unittest.skip("Exercise 4")
    def test_productview_nonexisting_id(self):
        response = self.client.get('/products/%d/'%(random.randint(100, 200)))
        self.assertEquals(response.status_code, 404, "Testing that a nonexisting product id returns 404 response code")
