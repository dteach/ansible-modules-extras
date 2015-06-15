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
    from Exscript import Account, Host
    from Exscript.util.start import start
except ImportError:
    exscript_found = False
else:
    exscript_found = True


class IOS(object):
    """IOS control class.  This uses Exscript to interact with IOS based devices
        Attributes:
            conn: ssh connection to IOS device"""
    conn = None


    def __init__(self, host, user, password, enable=False):
        acct = Account(name=user, password=password)
        if enable:
            acct.set_authorization_password(enable)
        host = Host('ssh://' + host)
        host.set_option('driver', 'ios')
        start(acct, host, self.init_conn, **{'verbose':0})

    def init_conn(self, job, host, conn):
        #prepare the device to send and receive commands
        inited = conn.autoinit()
        self.conn = conn
        print job
        print host
        print conn
        print self.conn

        return

    def get_conn(self):
        return self.conn

class Version(object):
    conn = None

    def __init__(self, ios):
        self.conn = ios.get_conn()

    def get_version(self):
        pass

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


    ios_dev = IOS(host, user, password, enable)
    test_conn = ios_dev.get_conn()
    print ios_dev.conn
    print dir(test_conn)
    test_conn.execute('show version')
    print test_conn.response
    module.jsonify(ios_dev.response)

    #module.fail_json(msg="unknown failure while trying to run IOS: " + e)




from ansible.module_utils.basic import *

if __name__ == "__main__":
    main()