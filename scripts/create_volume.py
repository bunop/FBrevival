#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 13:42:27 2019

@author: Paolo Cozzi <cozzi@ibba.cnr.it>

Create a volume with python-digitalocean library (dev version). You will need
to set the DIGITALOCEAN_ACCESS_TOKEN environment variable

"""

import digitalocean

# define a volume object
volume = digitalocean.Volume(
    name="fb-volume",
    region="fra1",
    size_gigabytes=7,
    filesystem_type="ext4",
    filesystem_label="fb-volume")

# create a volume
volume.create()
