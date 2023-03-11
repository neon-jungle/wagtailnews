.. _setup:

=====
Setup
=====

``wagtailnews`` 2.x is compatible with Wagtail 2.15 or 2.16,
Django 3.0 and higher,
and Python 3.6 and higher.

For older version of Wagtail or Django, see past releases

For wagtail 3 and 4 check wagtailnews 3 and higher.

Step 1
______

Install ``wagtailnews`` using pip::

   pip install wagtailnews

Step 2
______

Add ``wagtailnews`` to your ``INSTALLED_APPS`` in settings:

.. code-block:: python

  INSTALLED_APPS += [
      'wagtailnews',
  ]
