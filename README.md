# SSH_CONFIG_AWS

this script will create your custom .ssh/config file based on your configuration of AWS. This file must be copy with correct name under .ssh/

this will configure the machines behind a NAT to use proxycommand. More info https://en.wikibooks.org/wiki/OpenSSH/Cookbook/Proxies_and_Jump_Hosts

you will need boto3 and AWS credentials configured

you will need to create the tmp folder under .ssh

Example of output file:
```
host NAT
        hostname 54.x.x.x
        User ec2-user
        IdentityFile    ~/.ssh/NAT.pem

host hostdemo01
        hostname 10.x.x.x
        ProxyCommand ssh -W %h:%p NAT
        StrictHostKeyChecking no
        ControlMaster auto
        ControlPath ~/.ssh/tmp/%h_%p_%r
        User centos
        IdentityFile    ~/.ssh/hostdemokey.pem
```
