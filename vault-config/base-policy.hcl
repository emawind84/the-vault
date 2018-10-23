# this policy is required for the correct execution of the vault manager
# you can register this policy with the following command:
# $ ./docker-auto.sh vault-cmd policy write policy=base /vault/config/base-policy.hcl
# then you can create a new token with the following command:
# $ ./docker-auto.sh vault-cmd token create -policy=base -orphan

path "pwdmng/*" {
  capabilities = ["create", "update", "read", "delete"]
}

# List existing secret engines.
path "sys/mounts"
{
  capabilities = ["read"]
}