"""
Mock utilities
"""


class MockResponse:
    """
    Base class to share methods
    """

    def __init__(self, status_code):
        self.status_code = status_code

    def json(self):
        raise NotImplementedError()

    @property
    def text(self):
        raise NotImplementedError()

    @property
    def ok(self):
        return self.status_code // 100 == 2


class MockTextResponse(MockResponse):
    """
    Mock an JSON HTTP response with a dict and a status code
    """

    def __init__(self, content, status_code):
        super().__init__(status_code)
        self.content = content

    def json(self):
        return {}

    @property
    def text(self):
        return self.content

    @property
    def ok(self):
        return self.status_code // 100 == 2


class MockJsonResponse(MockResponse):
    """
    Mock an JSON HTTP response with a dict and a status code
    """

    def __init__(self, json_data, status_code):
        super().__init__(status_code)
        self.json_data = json_data

    def json(self):
        return self.json_data

    @property
    def text(self):
        return str(self.json_data)
