import os
import hvac
from django.conf import settings

class Vault():
    PATH_PREFIX = 'secret/'
    client = hvac.Client(url=settings.VAULT_HOST, token=settings.VAULT_TOKEN)
    assert client.is_authenticated() # => True
    
    def delete(self, path):
        self.client.delete(self.PATH_PREFIX + path)

    def write(self, path, **kargs):
        self.client.write(self.PATH_PREFIX + path, **kargs)
        
    def read(self, path):
        return self.client.read(self.PATH_PREFIX + path)
