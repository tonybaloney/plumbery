[![Build status](https://img.shields.io/travis/bernard357/plumbery.svg)](https://travis-ci.org/bernard357/plumbery)  ![Python 2.7](https://img.shields.io/badge/python-2.7-blue.svg)

# plumbery

Are you looking for a cloud plumber? We hope that this one will be useful to
you.


## Infrastructure as code at Dimension Data with Apache Libcloud

* [Documentation of plumbery at ReadTheDocs](https://plumbery.readthedocs.org)
* Free software: Apache License (2.0)

## Features

* Run from the command line, or as a python library
* Read fittings plan in YAML
* Use cloud API to create the network infrastructure, and to build nodes
* Create network domains and Ethernet networks
* Reserve public IPv4 addresses
* Manage network address translation rules
* Manage firewall rules
* All images in libraries are available to new nodes
* Add multiple network interfaces to nodes
* Add public IPv4 addresses to nodes
* Add monitoring to nodes
* Build all blueprints
* Build a blueprint across multiple locations
* Start all nodes
* Start nodes belonging to the same blueprint
* Polish Linux nodes for quick bootstrapping
* Build a full inventory of nodes that have been deployed
* Reflect fittings into a ready-to-use inventory for ansible
* Stop all nodes
* Stop nodes belonging to the same blueprint
* Destroy all nodes
* Destroy nodes belonging to the same blueprint
* Many demonstration scripts are provided
* You can extend plumbery with your own polishers, it has been designed for that



