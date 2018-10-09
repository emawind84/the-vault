#backend "file" {
#  path = "/vault/file"
#}

storage "consul" {
  address = "consul:8500"
  path    = "vault/"
}

listener "tcp" {
 address     = "0.0.0.0:8200"
 tls_disable = 1
}