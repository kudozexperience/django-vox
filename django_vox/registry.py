import collections
import pydoc

from django.utils.translation import ugettext_lazy as _

from django_vox import settings

PROTOCOLS = {
    'email': _('Email'),
    'sms': _('SMS'),
    'slack-webhook': _('Slack Webhook'),
}


class BackendManager:

    def __init__(self, class_list):
        self.proto_map = collections.defaultdict(list)
        self.id_map = {}
        for cls in class_list:
            if cls.ID in self.id_map:
                raise RuntimeError(
                    'Conflicting backend IDs: {}'.format(cls.ID))
            self.proto_map[cls.PROTOCOL].append(cls)
            self.id_map[cls.ID] = cls

    def by_protocol(self, protocol: str):
        return self.proto_map[protocol]

    def by_id(self, id_val):
        return self.id_map[id_val]

    def all(self):
        return self.id_map.values()

    def protocols(self):
        return self.proto_map.keys()


BACKENDS = BackendManager(
    pydoc.locate(name) for name in settings.BACKENDS)


def get_protocol_choices():
    for protocol in BACKENDS.protocols():
        yield (protocol, PROTOCOLS.get(protocol, protocol))
