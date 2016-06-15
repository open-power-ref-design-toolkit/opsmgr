"""Ansible dict filters."""

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible.errors import AnsibleError


def error(msg, ignore=False):
    """Raise error unless errors should be ignored."""
    if ignore:
        return None
    else:
        raise AnsibleError(msg)


def get(data, path):
    """
    Recursively get the value of the key path `path` in `data`.

    Path should be a list of string keys. For each item in the path, a lookup
    will be performed.

    If the data is a dict, a normal key lookup will be performed.

    If the data is a list and the key is convertible to a number, the index
    will be returned. If the data is a list and the key is '*', the rest of
    the key path will be obtained from each item in the list.

    Parameters:
    `data` -- Nested dict or list.
    `path` -- List of string keys.
    """
    if len(path) <= 0:
        return data

    key, rest = path[0], path[1:]
    if isinstance(data, dict):
        return get(data[key], rest)
    elif isinstance(data, list):
        if key == '*':
            return [get(d, rest) for d in data]
        else:
            try:
                index = int(key)
            except:
                error("'%s' is not numeric index for list '%s'" % (key, data))
            return get(data[index], rest)
    else:
        raise AnsibleError("expected list or dict, got '%s'" % data)


def lookup(data, key, skip):
    """Look up the key path `key` in `data`.

    Parameters:
    `data` -- Nested dict or list.
    `key`  -- String path separated by '.'.
    `skip` -- Return none instead of raising errors when key path does not
              exist in `data`.
    """
    path = key.split(".")
    try:
        return get(data, path)
    except KeyError:
        error("could not find '%s' in '%s'" % (key, data), skip)
    except IndexError:
        error("index '%s' out of bounds in '%s'" % (key, data), skip)


def dictmap(items, schema, skip_absent=False):
    """
    Remap items into a dictionary described by `schema`.

    This constructs a dictionary for each item, based on the dictionary
    `schema`. Each path in the schema will be replaced by a lookup for that
    path.

    Parameters:
    `items`       -- A list of items.
    `schema`      -- A dictionary with names and paths.
    `skip_absent` -- If set to 'True', skips all instances that are missing
                     key or index values. If set to False, a partial object
                     will be return with only the matching values. Defaults to
                     False.
    """
    result = []
    for item in items:
        thing = {}
        for k, v in schema.items():
            value = lookup(item, v, skip_absent)
            if value is None and skip_absent:
                thing = None
                break
            thing[k] = value
        if thing is not None:
            result.append(thing)
    return result


class FilterModule(object):

    """Custom Megalomaniacs Ansible filters."""

    def filters(self):
        """Return available filter functions mapping."""
        return {
            'dictmap': dictmap,
        }
