=================================================
How to replicate a database across two locations?
=================================================

In this tutorial we will deploy a master database server and a slave
database server in a different location. The back-end IPv6 infrastructure
provided by Dimension Data will be used to replicate data continuously,
at no additional cost. With such redundancy, disaster recovery is limited
to the promotion of the slave database to a master database.

Requirements for this use case
------------------------------

* Deploy a master database in Netherlands
* Deploy a slave database in Germany
* Create a Network Domain at each location
* Create an Ethernet network at each location
* Allow IPv6 traffic from the master network to the slave network
* Deploy a SQL server at each location
* Add servers to the automated monitoring dashboard
* Assign public IPv4 addresses to each server
* Add address translation to ensure end-to-end IP connectivity
* Add firewall rule to accept TCP traffic on port 22 (ssh)


Fittings plan
-------------

Copy the text below and put it in a text file named ``fittings.yaml``:

.. sourcecode:: yaml

    ---
    safeMode: False
    ---
    # Amsterdam in Europe
    locationId: EU7
    regionId: dd-eu

    blueprints:

      # primary sql server
      - sql:
          domain:
            name: VDC1
            ipv4: 2
          ethernet:
            name: databases
            subnet: 10.0.0.0
            accept:
              - EU6::databases
          nodes:
            - masterSQL:
                description: '#sql #vdc1 #primary'
                appliance: 'RedHat 6 64-bit 4 CPU'
                glue:
                  - internet 22
                monitoring: essentials
                running: always

    ---
    # Frankfurt in Europe
    locationId: EU6
    regionId: dd-eu

    blueprints:

      # secondary sql server
      - sql:
          domain:
            name: VDC2
            ipv4: 2
          ethernet:
            name: databases
            subnet: 10.0.0.0
            accept:
              - EU7::databases
          nodes:
            - slaveSQL:
                description: '#sql #vdc2 #secondary'
                appliance: 'RedHat 6 64-bit 4 CPU'
                glue:
                  - internet 22
                monitoring: essentials


Please note that in this example both servers are exposed to public Internet.
In the real life this would probably not be the case, since database would
be accessed by application servers in the same locations.

Some notes on directives used in these fittings plan:

* ``appliance: 'RedHat 6 64-bit 4 CPU'`` - By default plumbery selects a bare
  Ubuntu image to create new nodes. This directive allows you to pick up an
  image available from the CloudControl library. You can
  prefer Linux node for some usages, and Windows for other usages. Plumbery
  is happy with any mix.

* ``running: always`` - The only way to stop the master database is either
  to shut it down from the CloudControl web interface, or from within a ssh
  session. Plumbery is prevented to stop this node, always.

* ``accept:`` - Since firewalls prevent traffic across networks by default,
  there is a need to list trusted sources of packets for each network. This
  is the purpose of this directive. In this case, we are accepting traffic from
  a network at another location, for example: ``EU7::databases``.


Deployment commands
-------------------

In this case, the blueprint ``sql`` is spread over two different
data centres. For this reason, plumbery will connect separately
to each data centre and to the dirty job to make you happy.

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml build
    $ python -m plumbery fittings.yaml start

These two commands will build fittings as per the provided plan, and start
servers as well. Look at messages displayed by plumbery while it is
working, so you can monitor what's happening.

Follow-up commands
------------------

At this stage the job is not finished. SQL software need to be actually
installed at each server. Also, replication has to be put in place between
the two servers.

Please refer to a good reference page on the topic, for example for MySQL
systems: http://plusbryan.com/mysql-replication-without-downtime

Destruction commands
--------------------

This is only a friendly reminder. If you were only testing this scenario,
would you consider to stop related costs when finish?

.. sourcecode:: bash

    $ python -m plumbery fittings.yaml stop
    $ python -m plumbery fittings.yaml destroy


