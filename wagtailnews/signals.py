from django.dispatch import Signal

newsitem_published = Signal()  # instance, created
newsitem_unpublished = Signal()  # instance
newsitem_draft_saved = Signal()  # instance, created
newsitem_deleted = Signal()  # instance
