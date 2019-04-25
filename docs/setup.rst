.. _setup:

=====
Setup
=====

``wagtailnews`` is compatible with Wagtail 2.3 and higher,
Django 1.11 and higher,
and Python 3.4 and higher.

For older version of Wagtail or Django, see past releases

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
      'wagtail.contrib.routable_page',
  ]
