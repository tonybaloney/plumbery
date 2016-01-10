#!/usr/bin/env python

"""
Tests for `text` module.
"""

import unittest
import yaml
from mock_api import DimensionDataMockHttp

from libcloud.compute.drivers.dimensiondata import DimensionDataNodeDriver

from plumbery.engine import PlumberyFittings, PlumberyEngine
from plumbery.facility import PlumberyFacility
from plumbery.text import PlumberyText, PlumberyContext, PlumberyNodeContext
from plumbery import __version__

input1 = """
var http = require('http');
http.createServer(function (req, res) {
  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end('Hello World\n');
}).listen(8080, '{{ node.private }}');
console.log('Server running at http://{{ node.private }}:8080/');
"""

expected1 = input1.replace('{{ node.private }}', '12.34.56.78')

input2 = {
    'packages': ['ntp', 'nodejs', 'npm'],
    'ssh_pwauth': True,
    'disable_root': False,
    'bootcmd': \
        ['curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -'],
    'write_files': [{
        'content': input1,
        'path': '/root/hello.js'}],
    'runcmd': ['sudo npm install pm2 -g', 'pm2 start /root/hello.js']}

expected2 = {
    'packages': ['ntp', 'nodejs', 'npm'],
    'ssh_pwauth': True,
    'disable_root': False,
    'bootcmd': \
        ['curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -'],
    'write_files': [{
        'content': expected1,
        'path': '/root/hello.js'}],
    'runcmd': ['sudo npm install pm2 -g', 'pm2 start /root/hello.js']}

input3 = """
disable_root: false
ssh_pwauth: True
bootcmd:
  - "curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -"
packages:
  - ntp
  - nodejs
  - npm
write_files:
  - content: |
      var http = require('http');
      http.createServer(function (req, res) {
        res.writeHead(200, {'Content-Type': 'text/plain'});
        res.end('Hello World\\n');
      }).listen(8080, '{{ node.public }}');
      console.log('Server running at http://{{ node.public }}:8080/');
    path: /root/hello.js
runcmd:
  - sudo npm install pm2 -g
  - pm2 start /root/hello.js
"""

expected3 = input3.replace('{{ node.public }}', '12.34.56.78')

input4 = """
locationId: EU6 # Frankfurt in Europe
regionId: dd-eu

blueprints:

  - nodejs:
      domain:
        name: NodejsFox
        service: essentials
        ipv4: 2
      ethernet:
        name: nodejsfox.servers
        subnet: 192.168.20.0
      nodes:
        - nodejs01:
            cpu: 2
            memory: 8
            monitoring: essentials
            glue:
              - internet 22 8080
            cloud-config:
              disable_root: false
              ssh_pwauth: True
              bootcmd:
                - "curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -"
              packages:
                - ntp
                - nodejs
                - npm
              write_files:
                - content: |
                    var http = require('http');
                    http.createServer(function (req, res) {
                      res.writeHead(200, {'Content-Type': 'text/plain'});
                      res.end('Hello World\\n');
                    }).listen(8080, '{{ node.public }}');
                    console.log('Server running at http://{{ node.public }}:8080/');
                  path: /root/hello.js
              runcmd:
                - sudo npm install pm2 -g
                - pm2 start /root/hello.js
"""

class FakeNode1:

    id = '1234'
    name = 'mongo_mongos01'
    public_ips = ['168.128.12.163']
    private_ips = ['192.168.50.11']
    extra = {'ipv6': '2a00:47c0:111:1136:47c9:5a6a:911d:6c7f',
             'datacenterId': 'EU6'}


class FakeNode2:

    id = '5678'
    name = 'mongo_mongos02'
    public_ips = ['168.128.12.164']
    private_ips = ['192.168.50.12']
    extra = {'ipv6': '2a00:47c0:111:1136:47c9:5a6a:911d:6c7f',
             'datacenterId': 'EU6'}


class FakeRegion:

    def list_nodes(self):
        return [FakeNode1(), FakeNode2()]

    def get_node(self, name):
        return FakeNode2()

class FakeFacility:

    plumbery = PlumberyEngine()
    region = FakeRegion()

    def list_nodes(self):
        return ['mongo_mongos01', 'mongo_mongos02']

    def power_on(self):
        pass

    def get_location_id(self):
        return 'EU6'

class FakeContainer:

    facility = FakeFacility()
    region = FakeRegion()


class TestPlumberyText(unittest.TestCase):

    def setUp(self):
        self.text = PlumberyText()

    def tearDown(self):
        pass

    def test_dictionary(self):

        template = "little {{ test }} with multiple {{test}} and {{}} as well"
        context = PlumberyContext(dictionary={ 'test': 'toast' })
        expected = "little toast with multiple toast and {{}} as well"
        self.assertEqual(
            self.text.expand_variables(template, context), expected)

    def test_engine(self):

        template = "we are running plumbery {{ plumbery.version }}"
        context = PlumberyContext(context=PlumberyEngine())
        expected = "we are running plumbery "+__version__
        self.assertEqual(
            self.text.expand_variables(template, context), expected)

    def test_input1(self):

        context = PlumberyContext(dictionary={ 'node.private': '12.34.56.78' })
        self.assertEqual(
            self.text.expand_variables(input1, context), expected1)

    def test_input2(self):

        context = PlumberyContext(dictionary={})
        transformed = yaml.load(self.text.expand_variables(input2, context))
        unmatched = {o : (input2[o], transformed[o])
            for o in input2.keys() if input2[o] != transformed[o]}
        if unmatched != {}:
            print(unmatched)
        self.assertEqual(len(unmatched), 0)

        context = PlumberyContext(dictionary={ 'node.private': '12.34.56.78' })
        transformed = yaml.load(self.text.expand_variables(input2, context))
        unmatched = {o : (expected2[o], transformed[o])
            for o in expected2.keys() if expected2[o] != transformed[o]}
        if unmatched != {}:
            print(unmatched)
        self.assertEqual(len(unmatched), 0)

    def test_input3(self):

        loaded = yaml.load(input3)
        context = PlumberyContext(dictionary={ 'node.public': '12.34.56.78' })
        transformed = yaml.load(self.text.expand_variables(loaded, context))
        self.assertEqual(transformed, yaml.load(expected3))

    def test_input4(self):

        loaded = yaml.load(input4)
        context = PlumberyContext(dictionary={})
        transformed = yaml.load(self.text.expand_variables(loaded, context))
        self.assertEqual(transformed, loaded)

    def test_node1(self):

        template = "{{ mongo_mongos01.public }}"
        context = PlumberyNodeContext(node=FakeNode1())
        expected = '168.128.12.163'
        self.assertEqual(
            self.text.expand_variables(template, context), expected)

        template = "{{mongo_mongos01.private }}"
        expected = '192.168.50.11'
        self.assertEqual(
            self.text.expand_variables(template, context), expected)

        template = "{{ mongo_mongos01}}"
        expected = '192.168.50.11'
        self.assertEqual(
            self.text.expand_variables(template, context), expected)

        template = "{{ mongo_mongos01.ipv6 }}"
        expected = '2a00:47c0:111:1136:47c9:5a6a:911d:6c7f'
        self.assertEqual(
            self.text.expand_variables(template, context), expected)

    def test_node2(self):

        template = "{{ mongo_mongos02.public }}"
        context = PlumberyNodeContext(node=FakeNode1(),
                                      container=FakeContainer())
        expected = '168.128.12.164'
        self.assertEqual(
            self.text.expand_variables(template, context), expected)

        template = "{{ mongo_mongos02.private }}"
        expected = '192.168.50.12'
        self.assertEqual(
            self.text.expand_variables(template, context), expected)

        template = "{{ mongo_mongos02 }}"
        expected = '192.168.50.12'
        self.assertEqual(
            self.text.expand_variables(template, context), expected)

        template = "{{ mongo_mongos02.ipv6 }}"
        expected = '2a00:47c0:111:1136:47c9:5a6a:911d:6c7f'
        self.assertEqual(
            self.text.expand_variables(template, context), expected)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())