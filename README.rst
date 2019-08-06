Fount
=====

`Fount`_ is an Apache2 licensed `Python web framework`_ for creating
single-page applications.

.. todo::

   - Embrace idea of components: web page can connect multiple components to
     different endpoints (micro-services!)
   - Support Django Channels, aiohttp, and others.
   - Support rendering as HTML for initial-load and fallback.
   - Add connect() api to Page which starts task to handle incoming messages,
     then update() broadcasts to all connected sockets.
   - Convert HTML to JSON on update().
   - Allow multiple components to share same websocket connection.
   - Use an asyncio queue for compatibility and publish/subscribe.
     - Scaling is a pub/sub problem. Would it work to make the queue external?
       - How would Google pub-sub work here?
     - Have input queue and output queue, output queue is drained at 60 FPS.
   - Page should have multiple Component(s) and a single web socket connection.
   - Messages should refer to Component using tag name, tag id, and tag class
     properties.
   - Events on the client side should be identified by component id then tag
     name, tag id, and tag class properties.
   - See also: https://anvil.works/
   - See also: https://github.com/flexxui/flexx

Testimonials
------------

Does your website or company use `Fount`_? Send us a `message
<contact@grantjenks.com>`_ and let us know.

Features
--------

- Pure-Python
- Developed on Python 3.7

.. todo::

   - Fully documented
   - 100% test coverage
   - Used in production at ???
   - Tested on CPython 3.5, 3.6, 3.7 and PyPy3
   - Compare with https://github.com/flexxui/flexx
   - Compare with https://www.reddit.com/r/Python/comments/cljawn/library_for_making_desktop_apps_like_react/

   .. image:: https://api.travis-ci.org/grantjenks/python-fount.svg?branch=master
      :target: http://www.grantjenks.com/docs/fount/

   .. image:: https://ci.appveyor.com/api/projects/status/github/grantjenks/python-fount?branch=master&svg=true
      :target: http://www.grantjenks.com/docs/fount/

Quickstart
----------

Installing `Fount`_ is simple with `pip
<https://pypi.org/project/pip/>`_::

    $ pip install fount

You can access documentation in the interpreter with Python's built-in `help`
function. The `help` works on modules, classes and methods in `Fount`_.

.. code-block:: python

    >>> import fount
    >>> help(fount)

User Guide
----------

.. todo::

   - Tutorial
   - API Reference
   - Case Study: Chat
   - Development

References
----------

- `Fount Documentation`_
- `Fount at PyPI`_
- `Fount at Github`_
- `Fount Issue Tracker`_

.. _`Fount Documentation`: http://www.grantjenks.com/docs/fount/
.. _`Fount at PyPI`: https://pypi.org/project/fount/
.. _`Fount at Github`: https://github.com/grantjenks/python-fount
.. _`Fount Issue Tracker`: https://github.com/grantjenks/python-fount/issues

Fount License
-------------

Copyright 2019 Grant Jenks

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License.  You may obtain a copy of the
License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied.  See the License for the
specific language governing permissions and limitations under the License.

.. _`Fount`: http://www.grantjenks.com/docs/fount/
.. _`Python web framework`: http://www.grantjenks.com/docs/fount/
