from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from .models import NEWSINDEX_MODEL_CLASSES


def user_can_edit_news_type(user, content_type):
    """ true if user has any permission related to this content type """
    if user.is_active and user.is_superuser:
        return True

    permission_codenames = content_type.permission_set.values_list('codename', flat=True)
    for codename in permission_codenames:
        permission_name = "%s.%s" % (content_type.app_label, codename)
        if user.has_perm(permission_name):
            return True

    return False


def user_can_edit_news(user):
    """ true if user has any permission related to any content type registered as a news type """
    newsitem_models = [model.get_newsitem_model()
                       for model in NEWSINDEX_MODEL_CLASSES]
    newsitem_cts = ContentType.objects.get_for_models(*newsitem_models).values()
    if user.is_active and user.is_superuser:
        # admin can edit news iff any news types exist
        return bool(newsitem_cts)

    permissions = Permission.objects.filter(content_type__in=newsitem_cts)\
        .select_related('content_type')
    for perm in permissions:
        permission_name = "%s.%s" % (perm.content_type.app_label, perm.codename)
        if user.has_perm(permission_name):
            return True

    return False
