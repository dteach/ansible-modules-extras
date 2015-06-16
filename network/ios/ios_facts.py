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


try:
    from Exscript import Account, Host, Queue
except ImportError:
    exscript_found = False
else:
    exscript_found = True


def do_work(job, host, conn):
    conn.execute('show version')
    return conn.response

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
    acct = Account(name=user, password=password)
    if enable:
        acct.set_authorization_password(enable)
    host = Host('ssh://' + host)
    host.set_option('driver', 'ios')
    queue = Queue(**{'verbose':0})
    queue.add_account(acct)
    task = queue.run(host,do_work)
    while not task.is_completed:
        pass
    queue.destroy()






from ansible.module_utils.basic import *

if __name__ == "__main__":
    main()