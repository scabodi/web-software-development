from django.contrib.auth import get_user, get_user_model
from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import ImproperlyConfigured
from django.db import IntegrityError
from django.http import HttpRequest
from django.test import TestCase, override_settings
from django.utils import translation
from django.forms.fields import CharField, Field, IntegerField
from django.contrib.auth.signals import user_login_failed
from unittest import mock

from .models import Profile

from django.contrib.auth.forms import (
    AdminPasswordChangeForm, AuthenticationForm, PasswordChangeForm,
    PasswordResetForm, ReadOnlyPasswordHashField, ReadOnlyPasswordHashWidget,
    SetPasswordForm, UserChangeForm, UserCreationForm,
)

class BasicTestCase(TestCase):
    def test_user(self):
        #Users can be created and can set their password
        u = User.objects.create_user('testuser', 'test@example.com', 'testpw')
        self.assertTrue(u.has_usable_password())
        self.assertFalse(u.check_password('bad'))
        self.assertTrue(u.check_password('testpw'))

        # Check an unusable password
        u.set_unusable_password()
        u.save()
        self.assertFalse(u.check_password('testpw'))
        self.assertFalse(u.has_usable_password())
        u.set_password('testpw')
        self.assertTrue(u.check_password('testpw'))
        u.set_password(None)
        self.assertFalse(u.has_usable_password())

        # Check username getter
        self.assertEqual(u.get_username(), 'testuser')

        # Check authentication/permissions
        self.assertFalse(u.is_anonymous)
        self.assertTrue(u.is_authenticated)
        self.assertFalse(u.is_staff)
        self.assertTrue(u.is_active)
        self.assertFalse(u.is_superuser)

        # Check API-based user creation with no password
        u2 = User.objects.create_user('testuser2', 'test2@example.com')
        self.assertFalse(u2.has_usable_password())

    def test_superuser(self):
        super = User.objects.create_superuser('super', 'super@example.com', 'super')
        self.assertTrue(super.is_superuser)
        self.assertTrue(super.is_active)
        self.assertTrue(super.is_staff)

    def test_superuser_no_email_or_password(self):
        cases = [
            {},
            {'email': ''},
            {'email': None},
            {'password': None},
        ]
        for i, kwargs in enumerate(cases):
            with self.subTest(**kwargs):
                superuser = User.objects.create_superuser(
                    'super{}'.format(i),
                    **kwargs
                )
                self.assertEqual(superuser.email, '')
                self.assertFalse(superuser.has_usable_password())

    def test_get_user_model(self):
        "The current user model can be retrieved"
        self.assertEqual(get_user_model(), User)

    def test_user_verbose_names_translatable(self):
        "Default User model verbose names are translatable"
        with translation.override('en'):
            self.assertEqual(User._meta.verbose_name, 'user')
            self.assertEqual(User._meta.verbose_name_plural, 'users')
        with translation.override('es'):
            self.assertEqual(User._meta.verbose_name, 'usuario')
            self.assertEqual(User._meta.verbose_name_plural, 'usuarios')


class TestGetUser(TestCase):

    def test_get_user_anonymous(self):
        request = HttpRequest()
        request.session = self.client.session
        user = get_user(request)
        self.assertIsInstance(user, AnonymousUser)

    def test_get_user(self):
        created_user = User.objects.create_user('testuser', 'test@example.com', 'testpw')
        self.client.login(username='testuser', password='testpw')
        request = HttpRequest()
        request.session = self.client.session
        user = get_user(request)
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, created_user.username)

class TestDataMixin:

    @classmethod
    def setUpTestData(cls):
        cls.u1 = User.objects.create_user(username='testclient', password='password', email='testclient@example.com')
        cls.u2 = User.objects.create_user(username='inactive', password='password', is_active=False)
        cls.u3 = User.objects.create_user(username='staff', password='password')
        cls.u4 = User.objects.create(username='empty_password', password='')
        cls.u5 = User.objects.create(username='unmanageable_password', password='$')
        cls.u6 = User.objects.create(username='unknown_password', password='foo$bar')


class UserCreationFormTest(TestDataMixin, TestCase):

    def test_user_already_exists(self):
        data = {
            'username': 'testclient',
            'password1': 'test123',
            'password2': 'test123',
        }
        form = UserCreationForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form["username"].errors,
                         [str(User._meta.get_field('username').error_messages['unique'])])

    def test_invalid_data(self):
        data = {
            'username': 'jsmith!',
            'password1': 'test123',
            'password2': 'test123',
        }
        form = UserCreationForm(data)
        self.assertFalse(form.is_valid())
        validator = next(v for v in User._meta.get_field('username').validators if v.code == 'invalid')
        self.assertEqual(form["username"].errors, [str(validator.message)])

    def test_password_verification(self):
        # The verification password is incorrect.
        data = {
            'username': 'jsmith',
            'password1': 'test123',
            'password2': 'test',
        }
        form = UserCreationForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form["password2"].errors,
                         [str(form.error_messages['password_mismatch'])])

    def test_both_passwords(self):
        data = {'username': 'jsmith'}
        form = UserCreationForm(data)
        required_error = [str(Field.default_error_messages['required'])]
        self.assertFalse(form.is_valid())
        self.assertEqual(form['password1'].errors, required_error)
        self.assertEqual(form['password2'].errors, required_error)

    @mock.patch('django.contrib.auth.password_validation.password_changed')
    def test_success(self, password_changed):
        # The success case.
        data = {
            'username': 'jsmith@example.com',
            'password1': 'Tiziocaio2',
            'password2': 'Tiziocaio2',
        }
        form = UserCreationForm(data)
        self.assertTrue(form.is_valid())
        form.save(commit=False)
        self.assertEqual(password_changed.call_count, 0)
        u = form.save()
        self.assertEqual(password_changed.call_count, 1)
        self.assertEqual(repr(u), '<User: jsmith@example.com>')

    @override_settings(AUTH_PASSWORD_VALIDATORS=[
        {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
        {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {
            'min_length': 12,
        }},
    ])
    def test_validates_password(self):
        data = {
            'username': 'testclient',
            'password1': 'testclient',
            'password2': 'testclient',
        }
        form = UserCreationForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form['password2'].errors), 2)
        self.assertIn('The password is too similar to the username.', form['password2'].errors)
        self.assertIn(
            'This password is too short. It must contain at least 12 characters.',
            form['password2'].errors
        )

    @override_settings(AUTH_PASSWORD_VALIDATORS=[
        {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    ])
    def test_user_create_form_validates_password_with_all_data(self):
        """UserCreationForm password validation uses all of the form's data."""
        class CustomUserCreationForm(UserCreationForm):
            class Meta(UserCreationForm.Meta):
                model = User
                fields = ('username', 'email', 'first_name', 'last_name')
        form = CustomUserCreationForm({
            'username': 'testuser',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'first_name': 'testpassword',
            'last_name': 'lastname',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['password2'],
            ['The password is too similar to the first name.'],
        )

    def test_username_field_autocapitalize_none(self):
        form = UserCreationForm()
        self.assertEqual(form.fields['username'].widget.attrs.get('autocapitalize'), 'none')

    def test_html_autocomplete_attributes(self):
        form = UserCreationForm()
        tests = (
            ('username', 'username'),
            ('password1', 'new-password'),
            ('password2', 'new-password'),
        )
        for field_name, autocomplete in tests:
            with self.subTest(field_name=field_name, autocomplete=autocomplete):
                self.assertEqual(form.fields[field_name].widget.attrs['autocomplete'], autocomplete)

@override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.AllowAllUsersModelBackend'])
class AuthenticationFormTest(TestDataMixin, TestCase):

    def test_invalid_username(self):
        # The user submits an invalid username.

        data = {
            'username': 'jsmith_does_not_exist',
            'password': 'test123',
        }
        form = AuthenticationForm(None, data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.non_field_errors(), [
                form.error_messages['invalid_login'] % {
                    'username': User._meta.get_field('username').verbose_name
                }
            ]
        )

    def test_inactive_user(self):
        # The user is inactive.
        data = {
            'username': 'inactive',
            'password': 'password',
        }
        form = AuthenticationForm(None, data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.non_field_errors(), [str(form.error_messages['inactive'])])

    # Use an authentication backend that rejects inactive users.
    @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
    def test_inactive_user_incorrect_password(self):
        """An invalid login doesn't leak the inactive status of a user."""
        data = {
            'username': 'inactive',
            'password': 'incorrect',
        }
        form = AuthenticationForm(None, data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.non_field_errors(), [
                form.error_messages['invalid_login'] % {
                    'username': User._meta.get_field('username').verbose_name
                }
            ]
        )

    def test_login_failed(self):
        signal_calls = []

        def signal_handler(**kwargs):
            signal_calls.append(kwargs)

        user_login_failed.connect(signal_handler)
        fake_request = object()
        try:
            form = AuthenticationForm(fake_request, {
                'username': 'testclient',
                'password': 'incorrect',
            })
            self.assertFalse(form.is_valid())
            self.assertIs(signal_calls[0]['request'], fake_request)
        finally:
            user_login_failed.disconnect(signal_handler)

class SetPasswordFormTest(TestDataMixin, TestCase):

    def test_password_verification(self):
        # The two new passwords do not match.
        user = User.objects.get(username='testclient')
        data = {
            'new_password1': 'abc123',
            'new_password2': 'abc',
        }
        form = SetPasswordForm(user, data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form["new_password2"].errors,
            [str(form.error_messages['password_mismatch'])]
        )

    @mock.patch('django.contrib.auth.password_validation.password_changed')
    def test_success(self, password_changed):
        user = User(username="Holachico")
        data = {
            'new_password1': 'TizioCaio1',
            'new_password2': 'TizioCaio1',
        }
        form = SetPasswordForm(user, data)
        self.assertTrue(form.is_valid())
        form.save(commit=False)
        self.assertEqual(password_changed.call_count, 0)
        form.save()
        self.assertEqual(password_changed.call_count, 1)

    @override_settings(AUTH_PASSWORD_VALIDATORS=[
        {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
        {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {
            'min_length': 12,
        }},
    ])
    def test_validates_password(self):
        user = User.objects.get(username='testclient')
        data = {
            'new_password1': 'testclient',
            'new_password2': 'testclient',
        }
        form = SetPasswordForm(user, data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form["new_password2"].errors), 2)
        self.assertIn('The password is too similar to the username.', form["new_password2"].errors)
        self.assertIn(
            'This password is too short. It must contain at least 12 characters.',
            form["new_password2"].errors
        )
