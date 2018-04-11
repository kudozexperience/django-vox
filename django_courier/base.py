import abc
from typing import Any, Iterable, List, TypeVar


class Contact:
    """A generic contact object

    If you want to return something that looks like this, make sure
    to implement the __hash__ method the same, otherwise filtering
    duplicate contacts won't work
    """

    def __init__(self, name: str, protocol: str, address: str, obj: Any=None):
        self.name = name
        self.protocol = protocol
        self.address = address
        self.object = obj

    def __str__(self):
        return '{} <{}:{}>'.format(self.name, self.protocol, self.address)

    def __hash__(self):
        return hash(str(self))


class AbstractContactable(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_contacts_for_notification(
            self, notification: 'Notification') -> List[Contact]:
        ...


class AbstractContactNetwork(metaclass=abc.ABCMeta):

    def get_contactables(self, channel: str) -> List[AbstractContactable]:
        ...


class ContactNetwork:

    def get_contactables(self, channel: str) -> Iterable[AbstractContactable]:
        if channel == '':
            return (self,)
        raise ValueError('Channel {} not supported'.format(channel))


AbstractContactable.register(ContactNetwork)
AbstractContactNetwork.register(ContactNetwork)


AbstractContactNetworkN = TypeVar('AbstractContactNetworkN',
                                  AbstractContactNetwork, None)
