from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from db.models import Rabbit


class HomeViewTests(TestCase):
    def setUp(self):
        # create two bucks that will later be selected simultaneously
        # leave the birthday blank so the animals aren't included in the
        # 'rabbit cards' on the homepage; that prevents the template from
        # trying to access an image URL on a record that has none.
        self.buck1 = Rabbit.objects.create(
            name='Buck1',
            date_of_birth=None,
            sex='M',
        )
        self.buck2 = Rabbit.objects.create(
            name='Buck2',
            date_of_birth=None,
            sex='M',
        )

    def test_multiple_bucks_error(self):
        """Posting a new rabbit with two bucks should result in an error message."""
        img = SimpleUploadedFile('test.jpg', b'fakecontent', content_type='image/jpeg')
        response = self.client.post(
            reverse('home'),
            {
                'name': 'Baby',
                'date_of_birth': '2021-01-01',
                'sex': 'M',
                'parent_ids': f'{self.buck1.id},{self.buck2.id}',
                'image': img,
            },
        )
        # view redirects back to home on error
        self.assertRedirects(response, reverse('home'))
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('Only one Buck' in m.message for m in messages))
