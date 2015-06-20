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
import re


RE_VER = [
    re.compile(r'(System\ )(restarted.*|image.*)'),
    re.compile(r'(?:.*Cisco.*|.*Technical.*|.*laws.*)'),
    re.compile(r'([A-Z].*:)\s(.*)\s?'),
    re.compile(r'(.*uptime\sis)(.*)'),
    re.compile(r'(/d+)(.*interfaces?)'),
    re.compile(r'(.*WS.*?)\s+([\d.()A-Z]+)'),
          ]

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

    def add_hosts(self, hosts, default_protocol = "ssh2", default_driver = 'ios', default_port = 22):
        for host in hosts.split(','):
            tmp_host = Host(host)
            tmp_host.set_protocol(default_protocol)
            tmp_host.set_option('driver', default_driver)
            tmp_host.set_tcp_port(default_port)
            self.hosts.append(tmp_host)

    def add_accounts(self, name, password, enable=False):
        acct = Account(name=name, password=password)
        if enable:
            acct.set_authorization_password(enable)
        return self.q.add_account(acct)
        
    def run(self, func):
        self.q.run(self.hosts, autologin()(func))

    def destroy(self):
        self.q.destroy()



class getFacts(object):

    results = None

    def __init__(self):
        self.results = {}

    def add_host(self, host):
        self.results[host] = {}

    def add_cmd(self, host, cmd):
        self.results[host] = {cmd: ""}

    def add_resp(self, host, cmd, resp):
        self.results[host][cmd] = resp

    def has_host(self, host):
        return host in self.results

    def has_cmd(self, host, cmd):
        return cmd in self.results[host]

    def get_results(self):
        return self.results


def func_factory(job, host, conn, funct_list, facts):
    func_facts = facts
    for func in funct_list:
        conn.autoinit()
        func(host, conn, func_facts)


def get_ver(host, conn, my_facts):
    cmd = 'show version'
    hn = host.get_name()
    if not my_facts.has_host(hn):
        my_facts.add_host(hn)
    if not my_facts.has_cmd(hn, cmd):
        my_facts.add_cmd(hn, cmd)
    conn.execute(cmd)
    parsed = parse_ver(conn.response)
    print(parsed.groups())
    my_facts.add_resp(hn, cmd, parsed)


def parse_ver(str):
    for line in str.split('\r\n'):
        print repr(line)
        for re in RE_VER:
            res = re.match(line)
            if res:
                print RE_VER[RE_VER.index(re)].pattern
                print res.groups()
                break
    return str


def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(type='str', required=True),
            user=dict(type='str', required=True),
            password=dict(type='str', required=True),
            enable=dict(type='str', required=False),
        )
    )


    if not exscript_found:
        module.fail_json(msg="the python module 'exscript' is required")

    host = module.params['host']
    user = module.params['user']
    password = module.params['password']
    enable = module.params['enable']
    #use the Queue module form exscript to run through all of the hosts
    my_devs = dev_q(**{'verbose': 0})
    my_devs.add_hosts(host)
    my_devs.add_accounts(user, password, enable)
    my_facts = getFacts()
    try:
        my_devs.run(bind(func_factory, [get_ver],my_facts))
        my_devs.destroy()
        print my_facts.get_results()
    except:
        module.fail_json(msg=str(sys.exc_info()))







from ansible.module_utils.basic import *

if __name__ == "__main__":
    main()
