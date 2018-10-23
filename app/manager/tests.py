from django.test import TestCase

from .vault import VaultClient

class VaultTest(TestCase):

    TEST_MOUNT_POINT='test/'

    def setUp(self):
        self.vault_client = VaultClient(mount_point=self.TEST_MOUNT_POINT)

    def test_vault_write(self):
        self.vault_client.write('test1', abc='val1')

    def test_vault_read(self):
        self.vault_client.write('test1', abc='val1')

        data = self.vault_client.read('test1')
        self.assertIsNotNone(data)
        self.assertIn('data', data)
        self.assertIn('abc', data['data'])

    def test_vault_delete(self):
        self.vault_client.write('test1', abc='val1')
        self.vault_client.delete('test1')
        data = self.vault_client.read('test1')
        self.assertIsNone(data)

    def test_vault_wrap(self):
        response = self.vault_client.wrap({'abc': 'val1'})
        self.assertIsNotNone(response)
        self.assertIn('wrap_info', response)
        
    def test_vault_unwrap(self):
        response = self.vault_client.wrap({'abc': 'val1'})
        token = response['wrap_info']['token']

        unwrapped_data = self.vault_client.unwrap(token)
        self.assertIsNotNone(unwrapped_data)
        self.assertIn('data', unwrapped_data)
        self.assertIn('abc', unwrapped_data['data'])