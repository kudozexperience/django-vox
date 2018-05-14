import collections
import pydoc

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from django_vox import settings

PROTOCOLS = {
    'email': _('Email'),
    'sms': _('SMS'),
    'slack-webhook': _('Slack Webhook'),
    'json-webhook': _('JSON Webhook'),
    'twitter': _('Twitter'),
    'xmpp': _('XMPP'),
}

PREFIX_NAMES = {
    'si': _('Site Contacts'),
    'c': '__content__',
    'se': _('Source'),
    're': _('Target'),
}
PREFIX_FORMATS = {
    'c': '{}',
    'se': _('Source\'s {}'),
    're': _('Target\'s {}'),
}

_CHANNEL_TYPE_IDS = None


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


UnboundChannel = collections.namedtuple(
    'UnboundChannel', ('name', 'target_class', 'func'))


class Channel:
    def __init__(self, ubc: UnboundChannel, obj):
        self.name = ubc.name
        self.target_class = ubc.target_class
        self.func = ubc.func
        self.obj = obj

    def contactables(self):
        return (self.obj,) if self.func is None else self.func(self.obj)


class UnboundChannelMap(dict):

    def bind(self, obj):
        return BoundChannelMap(
            ((key, Channel(ubc, obj)) for (key, ubc) in self.items()))


class BoundChannelMap(dict):
    pass


class ChannelManagerItem:

    def __init__(self, cls):
        self.cls = cls
        self.__prefixes = {}
        self._channels = collections.defaultdict(dict)

    def add(self, key, name, target_type, func):
        self._channels[key] = name, target_type, func
        self.__prefixes = {}

    def add_self(self):
        self.add('', '', self.cls, None)

    def prefix(self, prefix) -> UnboundChannelMap:
        # get channels by prefix
        if prefix not in self.__prefixes:
            ubc_map = UnboundChannelMap()
            for key, (name, cls, func) in self._channels.items():
                channel_key = prefix if key == '' else prefix + ':' + key
                if name == '':
                    name = PREFIX_NAMES[prefix]
                    if name == '__content__':
                        name = self.cls._meta.verbose_name.title()
                else:
                    name = PREFIX_FORMATS[prefix].format(name)
                ubc_map[channel_key] = UnboundChannel(name, cls, func)
            self.__prefixes[prefix] = ubc_map
        return self.__prefixes[prefix]


class ChannelManager(dict):

    def __missing__(self, key):
        item = ChannelManagerItem(key)
        self[key] = item
        return item


backends = BackendManager(
    pydoc.locate(name) for name in settings.BACKENDS)

channels = ChannelManager()


def get_protocol_choices():
    for protocol in backends.protocols():
        yield (protocol, PROTOCOLS.get(protocol, protocol))


def _channel_type_ids():
    for all_models in apps.all_models.values():
        for model in all_models.values():
            if model in channels:
                ct = ContentType.objects.get_for_model(model)
                yield ct.id


def channel_type_limit():
    global _CHANNEL_TYPE_IDS
    if _CHANNEL_TYPE_IDS is None:
        _CHANNEL_TYPE_IDS = tuple(_channel_type_ids())
    return {'id__in': _CHANNEL_TYPE_IDS}
