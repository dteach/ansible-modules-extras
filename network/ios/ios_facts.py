#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2013, Matt Hite <mhite@hotmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

import sys
import json
try:
    from Exscript import Account, Host, Queue
    from Exscript.util.decorator import autologin, bind

except ImportError:
    exscript_found = False
else:
    exscript_found = True

class dev_q(object):
    q = None
    hosts = None

    def __init__(self, **kwargs):
        self.q = Queue(**kwargs)
        self.hosts = []

    def add_hosts(self, hosts, default_protocol = "ssh", default_driver = 'ios'):
        for host in hosts.split(','):
            tmp_host = Host(host)
            tmp_host.set_protocol(default_protocol)
            tmp_host.set_option('driver', default_driver)
            self.hosts.append(tmp_host)

    def add_accounts(self, name, password, enable=False):
        acct = Account(name=name, password=password)
        if enable:
            acct.set_authorization_password(enable)
        return self.q.add_account(acct)
        
    def run(self, func):
        return self.q.run(self.hosts, autologin()(func))

class getFacts(object):
    results = None

    def __init__(self):
        self.results = {}

    def add_results(self, host, response):
        self.results[host] = response

    def get_results(self):
        return self.results


def get_ver(job, host, conn, my_facts):
    print "do we get here"
    print host
    print conn
    conn.autoinit()
    conn.execute('show version')
    print conn.response
    my_facts.add_results(host, conn.response)

def main():
    module = AnsibleModule(
        argument_spec = dict(
            host = dict(type='str', required=True),
            user = dict(type='str', required=True),
            password = dict(type='str', required=True),
            enable = dict(type='str', required=False),
        )
    )


    if not exscript_found:
        module.fail_json(msg="the python module 'exscript' is required")

    host = module.params['host']
    user = module.params['user']
    password = module.params['password']
    enable = module.params['enable']
    #use the Queue module form exscript to run through all of the hosts
    my_devs = dev_q(**{'verbose': 2})
    my_devs.add_hosts(host)
    my_devs.add_accounts(user, password, enable)
    my_facts = getFacts()
    my_devs.run(bind(get_ver, my_facts))







from ansible.module_utils.basic import *

if __name__ == "__main__":
    main()