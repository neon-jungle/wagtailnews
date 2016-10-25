.. _setup:

=====
Setup
=====

``wagtailnews`` is compatible with Wagtail 1.6 and higher,
Django 1.9 and higher,
and Python 2.7 and Python 3.4 and higher.

Step 1
______

Install ``wagtailnews`` using pip::

   pip install wagtailnews

Step 2
______

Add ``wagtailnews`` and ``wagtail.contrib.wagtailroutablepage`` to your ``INSTALLED_APPS`` in settings:

.. code-block:: python

  INSTALLED_APPS += [
      'wagtailnews',
      'wagtail.contrib.wagtailroutablepage',
  ]
