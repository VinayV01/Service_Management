from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Services


def make_service(name='Hair Cut', price=200, duration=30, status='active'):
    return Services.objects.create(
        service_name=name, description='test', price=price, duration=duration, status=status
    )


class ServiceAPITests(APITestCase):

    def setUp(self):
        self.service = make_service()
        self.list_url = reverse('api_service_list')
        self.detail_url = reverse('api_service_detail', args=[self.service.pk])

    def test_create_service(self):
        data = {'service_name': 'Facial', 'price': '500.00', 'duration': 45, 'status': 'active'}
        res = self.client.post(self.list_url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Services.objects.count(), 2)

    def test_create_with_invalid_data(self):
        data = {'service_name': 'ab', 'price': '-5', 'duration': 0}
        res = self.client.post(self.list_url, data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('service_name', res.data)
        self.assertIn('price', res.data)
        self.assertIn('duration', res.data)

    def test_duplicate_name_not_allowed(self):
        data = {'service_name': 'hair cut', 'price': '100', 'duration': 20}
        res = self.client.post(self.list_url, data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_is_paginated(self):
        for i in range(7):
            make_service(name=f'Service {i}')
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 8)
        self.assertEqual(len(res.data['results']), 5)
        self.assertIsNotNone(res.data['next'])

    def test_search_and_filter(self):
        make_service(name='Massage', status='inactive')
        res = self.client.get(self.list_url, {'search': 'mass'})
        self.assertEqual(res.data['count'], 1)
        res = self.client.get(self.list_url, {'status': 'inactive'})
        self.assertEqual(res.data['count'], 1)
        self.assertEqual(res.data['results'][0]['service_name'], 'Massage')

    def test_detail(self):
        res = self.client.get(self.detail_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['service_name'], 'Hair Cut')

    def test_invalid_ids(self):
        res = self.client.get(reverse('api_service_detail', args=[999]))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        res = self.client.get(reverse('api_service_detail', args=['abc']))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update(self):
        res = self.client.patch(self.detail_url, {'price': '250.00'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.service.refresh_from_db()
        self.assertEqual(str(self.service.price), '250.00')

    def test_delete(self):
        res = self.client.delete(self.detail_url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Services.objects.exists())


class ServicePanelTests(TestCase):

    def setUp(self):
        self.service = make_service()

    def test_home_page(self):
        make_service(name='Massage', status='inactive')
        res = self.client.get(reverse('home'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['total'], 2)
        self.assertEqual(res.context['active'], 1)
        self.assertEqual(res.context['inactive'], 1)

    def test_list_page(self):
        res = self.client.get(reverse('service_list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Hair Cut')

    def test_search_and_status_filter(self):
        make_service(name='Massage', status='inactive')
        res = self.client.get(reverse('service_list'), {'q': 'mass', 'status': 'inactive'})
        self.assertContains(res, 'Massage')
        self.assertNotContains(res, 'Hair Cut')

    def test_add_service(self):
        data = {'service_name': 'Facial', 'description': '', 'price': '400', 'duration': 40, 'status': 'active'}
        res = self.client.post(reverse('service_create'), data)
        self.assertRedirects(res, reverse('service_list'))
        self.assertTrue(Services.objects.filter(service_name='Facial').exists())

    def test_add_service_invalid(self):
        data = {'service_name': '', 'price': '0', 'duration': 0, 'status': 'active'}
        res = self.client.post(reverse('service_create'), data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.context['form'].errors)

    def test_edit_service(self):
        data = {'service_name': 'Hair Cut', 'description': 'x', 'price': '300', 'duration': 30, 'status': 'inactive'}
        res = self.client.post(reverse('service_update', args=[self.service.pk]), data)
        self.assertRedirects(res, reverse('service_detail', args=[self.service.pk]))
        self.service.refresh_from_db()
        self.assertEqual(self.service.status, 'inactive')

    def test_delete_service(self):
        res = self.client.post(reverse('service_delete', args=[self.service.pk]))
        self.assertRedirects(res, reverse('service_list'))
        self.assertFalse(Services.objects.exists())

    def test_invalid_id_gives_404(self):
        res = self.client.get(reverse('service_detail', args=[999]))
        self.assertEqual(res.status_code, 404)
