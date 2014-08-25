from wagtailnews.models import NEWSINDEX_MODEL_CLASSES


def newsindex(cls):
    NEWSINDEX_MODEL_CLASSES.append(cls)
    return cls
