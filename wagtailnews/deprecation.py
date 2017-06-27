import warnings


class DeprecatedCallableStr(str):
    do_no_call_in_templates = True

    def __new__(cls, value, *args, **kwargs):
        return super(DeprecatedCallableStr, cls).__new__(cls, value)

    def __init__(self, value, warning, warning_cls):
        self.warning, self.warning_cls = warning, warning_cls

    def __call__(self, *args, **kwargs):
        warnings.warn(self.warning, self.warning_cls, stacklevel=2)
        return str(self)

    def __repr__(self):
        super_repr = super(DeprecatedCallableStr, self).__repr__()
        return '<DeprecatedCallableStr {}>'.format(super_repr)
