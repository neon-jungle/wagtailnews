from django.utils.module_loading import import_module


class ModelViewProxy(object):

    view_module = None

    def __init__(self, view_path):
        self.view_path = view_path

    @property
    def views(self):
        if self.view_module is None:
            self.view_module = import_module(self.view_path)
        return self.view_module

    def __getattr__(self, name):
        return viewproxy(self, name).proxy()

    def __repr__(self):
        return '<ModelViewProxy "{0}">'.format(self.view_path)


class viewproxy(object):
    view = None

    def __init__(self, model_view_proxy, name):
        self.model_view_proxy = model_view_proxy
        self.name = name
        self.view = None

    def proxy(self):
        def proxy(page, request, *args, **kwargs):
            if self.view is None:
                self.view = getattr(self.model_view_proxy.views, self.name)
            return self.view(request, page, *args, **kwargs)
        return proxy
