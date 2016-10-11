#!/usr/bin/python
# -*- coding: utf-8 -*-
# -*- mode: python -*-

DOCUMENTATION = '''
'''

EXAMPLES = """
"""

from ansible import utils
from ansible import errors
from ansible.runner.return_data import ReturnData
from ansible.runner.action_plugins.include_vars import ActionModule as ActionBase


import sys

def dump(obj, nested_level=1, output=sys.stdout):
    spacing = '   '
    if type(obj) == dict:
        print >> output, '%s{' % ((nested_level) * spacing)
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print >> output, '%s%s:' % ((nested_level + 1) * spacing, k)
                dump(v, nested_level + 1, output)
            else:
                print >> output, '%s%s: %s' % ((nested_level + 1) * spacing, k, v)
        print >> output, '%s}' % (nested_level * spacing)
    elif type(obj) == list:
        print >> output, '%s[' % ((nested_level) * spacing)
        for v in obj:
            if hasattr(v, '__iter__'):
                dump(v, nested_level + 1, output)
            else:
                print >> output, '%s%s' % ((nested_level + 1) * spacing, v)
        print >> output, '%s]' % ((nested_level) * spacing)
    else:
        print >> output, '%s%s' % (nested_level * spacing, obj)


class ActionModule(ActionBase):
    
    TRANSFERS_FILES = False
    
    def __init__(self, runner):
        self.runner = runner
    
    def run(self, conn, tmp, module_name, module_args, inject, complex_args=None, **kwargs):
       
        retdata = super(ActionModule, self).run(conn, tmp, module_name, module_args, inject, complex_args, **kwargs)
 
        try:
            dump(retdata.result)
            data = dict()
            data['genesis'] = retdata.result
            result = dict()
            result['ansible_facts'] = data
            dump(result)
            return ReturnData(conn=conn, comm_ok=True, result=result)
        except:
            result = dict(failed=True, msg="Include has failed.")
            return ReturnData(conn=conn, comm_ok=True, result=result)


