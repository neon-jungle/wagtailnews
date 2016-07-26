def model_string(model):
    return '{}.{}'.format(model._meta.app_label, model._meta.model_name)
