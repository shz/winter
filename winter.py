'''
Winter
======
Simple migrations.  MIT license (see bottom).

Motivation
----------
Basically, you gotta handle schema changes.  This can be a bit of a hassle
with a document-based database like CouchDB, MongoDB, etc.  Winter helps ease
the pain by providing a straightforward and simple way to automatically handle
those changes.  It doesn't enforce a schema; it just lets you handle the
inevitable changes in document structure however you want to.

Usage
=====
Winter works with dict-like objects.  You define a series of migrations
by using simple function calls, and then just ask winter to run/initialize
migrations on those dicts.

    # Tells winter about a new object type
    winter.add('cricket')

    # First migration
    m = winter.migrate('cricket')
    m.add(foo='bar')

    # Second migration
    m = winter.migrate('cricket')
    m.rename(foo='baz')
    m.add(looks='butt ugly', intelligence='rather low')

    # Alternatively
    #    winter.migrate('cricket').rename(foo='baz').add(looks='butt ugly',
    #        intelligence='rather low')
    # This works because all migration methods return the migration, allowing
    # calls to be chained.

    # So now we have our migration for 'cricket' defined.  Now, when we
    # create or use 'cricket' objects, we need to make a call using
    # Winter, which will blah blah blah TODO
    cricket = winter.objects.cricket({})

Changes are applied in the order they're defined.  Available changes:

 - add(name='default_value')
 - delete('field1', 'field2')
 - rename(original_name='new_name')
 - modify(field=lambda a: a + ' modified!')

Once objects are built out, they have a revision number attached to
them (called '_winter').  When more transitions are added in the future,
that object will only be updated with transitions there were added
after its revision number.  This allows Winter to migrate objects
pulled from a database, for example.

When working with multiple developers who need to make schema changes
to the same object, they should all work off of one migration file, and simply
add their changes to the bottom.  When they merge their changes back with
trunk (or master, if you're a git), they just need to merge in order and all
is well.  The migration file defines the process.
'''

# Make stuff work in 2/3
from __future__ import print_function

# Other imports
import uuid
import hashlib
import sys

# Cross-version function for determining if the argument is callable
if sys.hexversion > 0x03000000:
    import collections

    def _callable(f):
        return isinstance(f, collections.Callable)
else:
    def _callable(f):
        return callable(f)


class MigrationManager(object):
    def __init__(self, name):
        # Revisions is a dict from revision id to the next revision id
        # in sequence.
        self.revisions  = {}
        # Migrations is a dict from revision to migration
        self.migrations = {}
        self.base_hash = hashlib.sha1()
        self.base_hash.update(name.encode('utf-8'))
        self.name = name
        # Newest revision
        self.head = self.base_hash.hexdigest()

    def add(self, migration):
        '''
        Adds a new migration to the chain.
        '''
        # Create a new hash for this migration
        new_rev = self.base_hash.copy()
        new_rev.update(str(len(self.revisions)).encode('utf-8'))
        new_rev = new_rev.hexdigest()
        # Update the revision trail
        self.revisions[self.head] = new_rev
        # ...and assign this new revision to head
        self.head = new_rev

        # Store this migration
        self.migrations[new_rev] = migration

    def migrate(self, obj):
        '''
        Migrates an object from its current revision to the latest
        revision.
        '''
        if not '_winter' in obj:
            obj['_winter'] = self.base_hash.copy().hexdigest()

        rev = obj['_winter']
        while rev != self.head:
            # Sanity check on the revision
            if not rev in self.revisions:
                raise Exception("Dead end revision %s" % rev)

            # Grab the revision following the obj's revision
            rev = self.revisions[rev]
            # Update the object to this revision
            self.migrations[rev].apply(obj)
            obj['_winter'] = rev


class Migration(object):

    # These class methods perform the actual actions
    @classmethod
    def _add(cls, obj, field, value):
        obj[field] = value

    @classmethod
    def _delete(cls, obj, field):
        del obj[field]

    @classmethod
    def _rename(cls, obj, field, name):
        obj[name] = obj[field]
        del obj[field]

    @classmethod
    def _modify(cls, obj, field, f):
        obj[field] = f(obj[field])

    # We now return you to your regularly scheduled class
    def __init__(self):
        # The list of actions to run on an object.  This list contains
        # tuples of the form (migration_function, field_name, *args).
        self._actions = []


    def add(self, **kwargs):
        '''
        Adds fields, using key/value pairs.
        '''
        for field, value in kwargs.items():
            self._actions.append((Migration._add, field, value))
        return self

    def delete(self, *args):
        '''
        Deletes fields.
        '''
        for field in args:
            self._actions.append((Migration._delete, field))
        return self

    def rename(self, **kwargs):
        '''
        Renames fields
        '''
        for name1, name2 in kwargs.items():
            #sanity check
            if name1 == name2:
                raise Exception('Attempting to rename field "%s" to the same name' % name1)
            self._actions.append((Migration._rename, name1, name2))
        return self

    def modify(self, *args, **kwargs):
        '''
        Modifies fields with an arbitrary function.

        Named arguments are used to define migrations on each field; the
        argument name is the field name, and the argument value is the
        function to apply to the field when migrating.
        '''
        for field, f in kwargs.items():
            # Sanity check
            if not _callable(f):
                raise Exception('Must supply a callable as a modifier for field %s' % field)
            self._actions.append((Migration._modify, field, f))
        return self

    def apply(self, obj):
        '''
        Applies the revision to an object.
        '''

        #apply the actions
        for action in self._actions:
            action[0](obj, *action[1:])

        return self

class Migrator(object):
    def __init__(self, type):
        self._type = type

    def tag(self, obj):
        '''
        Tags an object with the most recent winter revision, unless
        they already have a winter revision.
        '''
        if not '_winter' in obj:
            obj['_winter'] = managers[self._type].head
        return obj

    def __call__(self, obj):
        managers[self._type].migrate(obj)
        return obj

class WinterObjects(object):
    def __init__(self):
        self._cache = {}

    def __getattr__(self, key):
        if not key in managers:
            raise Exception("Winter doesn't have '%s' registered" % key)
        elif key in self._cache:
            return self._cache[key]
        else:
            self._cache[key] = Migrator(key)
            return self._cache[key]

    def __contains__(self, key):
        return key in managers

managers = {}
objects = WinterObjects()

def add(name):
    '''
    Creates an object in Winter with the given name
    '''
    #make sure this object isn't already added
    if name in managers:
        raise Exception("Object '%s' already added" % name)

    managers[name] = MigrationManager(name)

def migrate(name):
    '''
    Creates a new revision for the specified object with the given name
    '''
    if not name in managers:
        raise Exception("Object '%s' not registered with Winter; did you forget to call winter.add('%s')?" % s)

    m = Migration()
    managers[name].add(m)
    return m

# Here follows unrelated stuff that should be included with every good
# Python package:
#
#  * Test suite
#  * Distutils stuff
import sys

# The test suite.  If you're reading this to get a better feel for how
# to use winter.py, note that we're already inside the winter namespace.
if __name__ == '__main__' and len(sys.argv) == 1:
    print('Testing Winter...')

    # This is a pretty minimal test, but it should cover the majority of
    # the functionality.
    o = {}

    add('test1')

    # Addition!
    migrate('test1').add(a='a', b='b')
    o = objects.test1(o)

    assert('a' in o)
    assert(o['a'] == 'a')
    assert('b' in o)
    assert(o['b'] == 'b')

    # Renaming!
    migrate('test1').rename(a='c')
    o = objects.test1(o)

    assert(not 'a' in o)
    assert('c' in o)
    assert(o['c'] == 'a')
    assert('b' in o)
    assert(o['b'] == 'b')

    # Deletion!
    migrate('test1').delete('b')
    o = objects.test1(o)
    assert(not 'b' in o)

    # Modification!
    migrate('test1').modify(c=lambda x: x + x)
    o = objects.test1(o)
    assert(o['c'] == 'aa')

    # If we made it this far, then everything is kosher.
    print('Glorious Sucess')

# Installation
elif __name__ == '__main__' and sys.argv[1] == 'install':
    from distutils.core import setup
    setup(
        name='Winter',
        version='0.314',
        description='Dictionary Migrations',
        author='Patrick Stein',
        url='http://github.com/shz/winter',
        py_modules=['winter'],
    )

# The license (MIT)

'''
Copyright (c) 2012 Patrick Stein

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''
