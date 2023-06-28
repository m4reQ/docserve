import abc
import io
import pathlib
from xml import sax


class _XMLContentHandler(sax.ContentHandler):
    def __init__(self) -> None:
        self.char_data = io.StringIO()

    def characters(self, content):
        self.char_data.write(content)
        self.char_data.write(' ')

    @property
    def string_data(self) -> str:
        return self.char_data.getvalue()

class DocumentParser(abc.ABC):
    @abc.abstractmethod
    def parse(self, filepath: pathlib.Path) -> str: ...

class XMLParser(DocumentParser):
    def parse(self, filepath: pathlib.Path) -> str:
        assert filepath.exists(), "XML file does not exist"

        content_handler = _XMLContentHandler()

        sax.parse(filepath, content_handler)

        return content_handler.string_data

class TXTParser(DocumentParser):
    def parse(self, filepath: pathlib.Path) -> str:
        assert filepath.exists(), "TXT file does not exist"

        with open(filepath, 'r') as f:
            return f.read()
