class Contact:
    """A generic contact object

    If you want to return something that looks like this, make sure
    to implement the __hash__ method the same, otherwise filtering
    duplicate contacts won't work
    """

    def __init__(self, name: str, protocol: str, address: str):
        self.name = name
        self.protocol = protocol
        self.address = address

    def __str__(self):
        return '{} <{}:{}>'.format(self.name, self.protocol, self.address)

    def __hash__(self):
        return hash(str(self))
