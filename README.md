FB Revival
==========

Steps to rise up a mirror of FruitBreedomics (FB) site

## Set up your environment variables

Please set your environment in order that scripts could work:

```
export DIGITALOCEAN_ACCESS_TOKEN=<your DO token>
```

## Create a droplet on Digital Ocean (DO)

Create a new droplet using:

```
$ python scripts/create_droplet.py
```

> NB: time is needed to start-up a droplet and to add firewalls, volumes, etc.
  the script will exit  if it can't perform a particoular action. Recall the
  script after the droplet is started to add additional configuration staff (the
  script make no changes if they currently applied on the droplet)

## Update `hosts` file

Set the current droplet IP address in `hosts` file:

```
[fruitbreedomics]
centos7     ansible_host=fb.paolocozzi.cloud
```

## Install all the roles:

```
$ ansible-playbook site.yml
```

The `openvz_role` was inspired from [here](https://www.sbarjatiya.com/notes_wiki/index.php/Automated_installation_of_OpenVZ_on_CentOS_using_ansible)

# Create a new container

Ensure a container is not present:

```
# vzlist -a 101
Container not found
```

create a new container with

```
$ vzctl create 100 --ostemplate centos-6-x86_64
$ vzctl set 100 --ipadd 192.168.0.100 --save
$ vzctl set 100 --nameserver 8.8.8.8 --save
$ vzctl set 100 --hostname server100.mydomain.com --save
```

Modify memory used:

```
$ vzctl set 109 --ram 1024M --save
```

Start the container and enter into it

```
$ vzctl start 100
$ vzctl enter 100
```

More info on basic operations could be found [here](https://wiki.openvz.org/User_Guide/Operations_on_Containers)
and [here](https://wiki.openvz.org/Basic_operations_in_OpenVZ_environment). Info on
[OpenVZ](https://docs.openvz.org/openvz_users_guide.webhelp/_openvz_overview.html).
Info on container [NAT](https://wiki.openvz.org/Using_NAT_for_container_with_private_IPs)
Info on changing memory [here](https://wiki.openvz.org/VSwap) and [here](https://chrisschuld.com/2009/09/adjusting-ram-for-an-openvz-vps/)
Info on [iptables](https://www.digitalocean.com/community/tutorials/iptables-essentials-common-firewall-rules-and-commands)

> **WARNING**: Not applied!
Info on [DHCP](https://wiki.openvz.org/DHCP) and [Virtual Ethernet device](https://wiki.openvz.org/Virtual_Ethernet_device)

# Restoring FB machine:

```
$ vzdump --restore /mnt/fb_volume/fruitbreedomics/vzdump-openvz-109-2019_06_12-22_10_52.tar.gz 109
$ vzctl set 109 --netif_del eth0 --save
$ vzctl set 109 --ipadd 192.168.0.109 --save
$ vzctl start 109
```
