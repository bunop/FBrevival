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
centos7     ansible_host=157.230.121.41
```

## Install all the roles:

```
ansible-playbook site.yml
```
