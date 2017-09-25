.. _signals:

=======
Signals
=======

Because news items are not wagtail pages, they can not react to wagtail hooks or
signals.  ``wagtailnews`` provides a set of ``django.dispatch`` signals for
easier extension and customizability.

.. code-block:: python

  from wagtailnews.signals import newsitem_published
  from django.dispatch import receiver

  @receiver(newsitem_published)
  def callback(sender, **kwargs):
      print('News item published!')

As with every other django signal, the ``sender`` and ``signal`` kwargs are
always included.

.. _newsitem_published:

``newsitem_published``
______________________

A signal sent out when a news item is published, with the following kwargs:

instance
    The newsitem that was just created
created
    Whether this publishing created the newsitem (This does not indicate that the newsitem was
    published for the first time, but that it was just created as a new database
    record.  This will only be set once across :ref:`newsitem_draft_saved` and
    this signal, depending which action is done first)

.. _newsitem_draft_saved:

``newsitem_draft_saved``
________________________

A signal sent out when a news item had a draft saved, with the following kwargs:

instance
    The newsitem that was just created
created
    Whether this publishing created the newsitem (see :ref:`newsitem_published`
    for some more information)

.. _newsitem_unpublished:

``newsitem_unpublished``
________________________

A signal sent out when a news item is unpublished, with the following kwargs:

instance
    The newsitem that was just created

.. _newsitem_deleted:

``newsitem_deleted``
____________________

A signal sent out when a news item is deleted, with the following kwargs:

instance
    The newsitem that was just created.  Be careful, this is the instance as-is
    after it has been deleted from the database, just like django's native
    ``post_delete`` signal.
