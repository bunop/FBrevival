#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 12:24:16 2019

@author: Paolo Cozzi <cozzi@ibba.cnr.it>

Create a droplet with python-digitalocean library (dev version). You will need
to set the DIGITALOCEAN_ACCESS_TOKEN environment variable

"""

import logging
import digitalocean

logging.basicConfig(
    format=(
        '%(asctime)s\t%(levelname)s:\t%(name)s line %(lineno)s\t%(message)s'),
    level=logging.DEBUG)

logger = logging.getLogger(__name__)

# some parameters
droplet_name = "FB-revival"

# get a manager object
manager = digitalocean.Manager()

droplet_found = False

# get all droplets
for droplet in manager.get_all_droplets():
    if droplet.name == droplet_name:
        logger.debug("Droplet found")
        droplet_found = True
        break

if not droplet_found:
    logger.info("Creating droplet '%s'" % droplet_name)
    # get all ssh keys
    keys = manager.get_all_sshkeys()

    droplet = digitalocean.Droplet(
        name=droplet_name,
        region='fra1',
        image='centos-7-x64',
        size_slug='s-1vcpu-1gb',
        ssh_keys=keys,
        monitoring=True
    )

    # create droplet
    droplet.create()

else:
    logger.info("Skipping droplet creation")

# these are active firewalls
# [<Firewall: f7460df0-da83-4d0e-bf34-d61a6b8e399d base>,
# <Firewall: 6e416d72-2c57-4ad7-bfc1-84f855dcda70 webserver>]

# get webserver firewall
firewall = manager.get_firewall("f7460df0-da83-4d0e-bf34-d61a6b8e399d")

if droplet.id not in firewall.droplet_ids:
    # add my droplet to this firewall
    logger.info(
        "Add droplet '%s' to firewall '%s'" % (droplet.name, firewall.name))
    firewall.add_droplets(droplet_ids=[droplet.id])

else:
    logger.info("Skipping firewall configuration")

# those are my current volumes
# [<Volume: 1e770393-8e9a-11e9-b6f5-0a58ac14d04f fb-volume 7>]

# get a volume object
volume = manager.get_volume("1e770393-8e9a-11e9-b6f5-0a58ac14d04f")

if droplet.id not in volume.droplet_ids:
    # add my droplet to this volume
    logger.info(
        "Add droplet '%s' to volume '%s'" % (droplet.name, volume.name))
    volume.attach(droplet_id=droplet.id, region="fra1")

else:
    logger.info("Skipping volume configuration")
