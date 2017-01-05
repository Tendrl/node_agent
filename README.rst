.. vim: tw=79

===================
 Tendrl Node Agent
===================

Tendrl node agent resides on every node managed by tendlr. It is
responsible for operating system level operations such as hardware
inventory, service management, process monitoring etc. The node agent
also serves as the provisioning controller and can invoke provisioning
operations on the node.

-  Free software: LGPL2

-  Documentation:
   https://github.com/Tendrl/node_agent/tree/master/doc/source

-  Source: https://github.com/Tendrl/node_agent

-  Bugs: https://github.com/Tendrl/node_agent/issues

|Build status| |Coverage|

Features
========

-  Provide Node hardware inventory (cpu, memory, processes etc) details
   in central store.

-  Implements operations Ceph/Gluster cluster import.

Builds
======

.. image:: https://travis-ci.org/Tendrl/node_agent.svg?branch=master
    :target: https://travis-ci.org/Tendrl/node_agent

Code Coverage
=============

.. image:: https://coveralls.io/repos/github/Tendrl/node_agent/badge.svg
    :target: https://coveralls.io/github/Tendrl/node_agent

Developer/Install documentation
===============================

We also have sphinx documentation in ``docs/source``.

*To build it, run:*

::

    $ python setup.py build_sphinx
