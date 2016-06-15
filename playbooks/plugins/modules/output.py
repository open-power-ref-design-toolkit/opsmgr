#!/usr/bin/python

DOCUMENTATION = '''
---
module: output
short_description: Prints output from a command execution
'''

EXAMPLES = '''
---
'''

from ansible.module_utils.basic import *
import requests

def main():

  fields = {
    "msg" : {"required" : true, "type" : "str" },
  }

  module = AnsibleModule(argument_spec=fields)
  module.exit_json(changed=true, meta=module.params)


if __name__ == '__main__':
    main()


