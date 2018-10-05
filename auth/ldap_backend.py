# mypackage.ldap

from django_auth_ldap.backend import LDAPBackend

class LDAPBackend1(LDAPBackend):
    settings_prefix = "AUTH_LDAP_1_"

class LDAPBackend2(LDAPBackend):
    settings_prefix = "AUTH_LDAP_2_"
