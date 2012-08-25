# winter.py

Simple dictionary migrations for Python

# About

winter.py is a small library designed to handle the problem of migrating
data in document-store databases like CouchDB or MongoDB.  It handles
field additions, deletions, renames, and arbitrary modifications to field
values.  It operates solely on Python dictionaries.

**Important:** `winter.py` is completely standalone.  The source file
               includes the license, documentation, a test suite, and
               distutils installer.  It has no dependencies, and works
               in Python 2.6+ and Python 3.0+.

# Installation

winter.py is a totally standalone module, so you can pick it up and drop
it wherever you want, and it'll import just fine.  If you're in the
mood, you can also install it as you would any other Python package by
the magic of good old distutils.  Just do

```bash
python winter.py install
```

Which is slightly unconventional, I know, but it lets me keep this down
to a single source file.

# Docs

Documentation lives at the top of the source file.  The test suite is
also pretty straightforward, so give that a look over if you're looking
for more guidance.

# License

The MIT License:

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
