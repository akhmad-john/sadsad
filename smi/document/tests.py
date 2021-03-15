import json
import os
from datetime import datetime

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model
from supply.account.payloads import get_test_user

from .models import DocumentModel
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

User = get_user_model()


def get_test_document(file_path=None):
    if file_path is None:
        file_path = os.path.join(settings.BASE_DIR, 'supply/core/files/vendor_product_template.xlsx')
    file = File(open(file_path, 'rb'))
    obj = DocumentModel.objects.create(file=file)
    return obj


def get_file_payload(file_path=None):
    if file_path is None:
        file_path = os.path.join(settings.BASE_DIR, 'supply/core/files/vendor_product_template.xlsx')
    file = File(open(file_path, 'rb'))
    uploaded_file = SimpleUploadedFile('testfile', file.read(),
                                       content_type='multipart/form-data')
    return dict(
        files=uploaded_file
    )


class DocumentUploadApiTest(APITestCase):

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    @classmethod
    def setUpTestData(cls):
        cls.user = get_test_user()
        cls.client = APIClient()

    def test_A_file_upload(self):
        url = reverse('documentmodel-list')
        response = self.client.post(url, get_file_payload(), format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.content)

