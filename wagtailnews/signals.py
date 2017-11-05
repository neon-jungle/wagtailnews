from django.dispatch import Signal

newsitem_published = Signal(providing_args=['instance', 'created'])
newsitem_unpublished = Signal(providing_args=['instance'])
newsitem_draft_saved = Signal(providing_args=['instance', 'created'])
newsitem_deleted = Signal(providing_args=['instance'])
