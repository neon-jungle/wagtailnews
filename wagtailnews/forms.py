from enum import Enum


class ActionSet(Enum):
    @classmethod
    def from_post_data(cls, data):
        for action in cls:
            if action.form_name in data:
                return action

        # Nothing found, return the first member as the default
        return next(iter(cls))

    @property
    def form_name(self):
        return 'action-' + self.name


class SaveActionSet(ActionSet):
    draft = 1
    publish = 2
    preview = 3
