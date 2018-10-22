#backend "file" {
#  path = "/vault/file"
#}

ui = true

storage "consul" {
  address = "consul:8500"
  path    = "vault/"
}

listener "tcp" {
 address     = "0.0.0.0:8200"
 tls_disable = 1
}

# by default a token last for a month, even if you try to renew it since the max ttl is a month,
# I want to be able to renew the token as much as I want.
max_lease_ttl = "99999h"