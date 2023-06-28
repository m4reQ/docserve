import collections
import dataclasses
import logging
import math
import pickle
import time
from concurrent import futures
from datetime import datetime
from pathlib import Path

from parsers import DocumentParser, TXTParser, XMLParser


@dataclasses.dataclass
class Document:
    '''
    Object that represents single documentation entry, containing all of
    basic informations.
    '''
    filepath: Path
    term_count: int
    last_modified: datetime
    term_frequency: dict[str, float] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_file(cls, filepath: Path):
        parser: DocumentParser
        match filepath.suffix.lower():
            case '.xml':
                parser = XMLParser()
            case '.txt':
                parser = TXTParser()
            case format:
                raise RuntimeError(f'Cannot parse unknown document format "{format}" (file: {filepath}).')

        string_data = parser.parse(filepath)
        terms = [x.lower() for x in string_data.replace('\n', ' ').replace('\t', ' ').split(' ') if x not in ('', '.', ',')]
        terms_count = len(terms)
        term_freq: dict[str, float] = {term: count / terms_count for term, count in collections.Counter(terms).items()}

        return cls(
            filepath,
            terms_count,
            datetime.fromtimestamp(filepath.stat().st_mtime),
            term_freq)

    def get_term_frequency(self, term: str) -> float:
        return self.term_frequency.get(term, 0.0)

    def contains_term(self, term: str) -> bool:
        return term in self.term_frequency

@dataclasses.dataclass
class QueryResult:
    original_query: str
    seconds_elapsed: float
    results: list[Document]

    @property
    def results_count(self) -> int:
        return len(self.results)

@dataclasses.dataclass
class Registry:
    '''
    Object that contains informations of all documentation files
    that are currently indexed. It allows to query for specific documents
    as well as making more advanced queries based on tf-idf algorithm.
    '''

    DEFAULT_REGISTRY_DATA_FILEPATH = Path('./registry.bin')

    docs: dict[Path, Document] = dataclasses.field(default_factory=dict)
    global_term_frequency: dict[str, float] = dataclasses.field(default_factory=dict) # number of documents containing the given word

    @classmethod
    def from_binary_file(cls, filepath: Path = DEFAULT_REGISTRY_DATA_FILEPATH):
        start = time.perf_counter()

        if not filepath.exists():
            _logger.warning('Registry binary file "%s" does not exist. Creating new registry...', filepath)
            return cls()

        with open(filepath, 'rb') as f:
            result = pickle.load(f)

        assert isinstance(result, cls), "Result object is not of the desired type."

        _logger.debug('Registry binary file loaded in %f seconds.', time.perf_counter() - start)

        return result

    def dump_to_binary_file(self, filepath: Path = DEFAULT_REGISTRY_DATA_FILEPATH) -> None:
        with open(filepath, 'wb+') as f:
            pickle.dump(self, f)

    def needs_reindexing(self, filepath: Path) -> bool:
        if filepath not in self.docs:
            return True

        return filepath.stat().st_mtime > self.docs[filepath].last_modified.timestamp()

    def add_documents_from_directory(self, directory: Path) -> None:
        assert directory.exists(), f'Documents directory "{directory}" does not exist.'

        start = time.perf_counter()

        to_reindex = [x for x in directory.glob('*') if x.is_file() and self.needs_reindexing(x)]
        with futures.ThreadPoolExecutor() as executor:
            documents = executor.map(Document.from_file, to_reindex)

        for doc in documents:
            self.docs[doc.filepath] = doc
            for term in doc.term_frequency:
                self.global_term_frequency[term] = sum(1 for x in self.docs.values() if x.contains_term(term)) / len(self.docs)

        _logger.debug(
            '%d document files loaded from directory "%s" in %f seconds.',
            len(to_reindex),
            directory,
            time.perf_counter() - start)

    def query(self, query_str: str, limit: int = 10) -> QueryResult:
        start = time.perf_counter()

        terms = [x for x in query_str.split(' ') if x not in ('', '.', ',')]

        ranking: list[tuple[float, Document]] = []
        for doc in self.docs.values():
            rank = 0.0
            for term in terms:
                rank += doc.get_term_frequency(term) * self._get_idf(term)

            ranking.append((rank, doc))

        ranking.sort(key=lambda x: x[0], reverse=True)
        results = [x[1] for x in ranking[:limit]]

        return QueryResult(query_str, time.perf_counter() - start, results)

    def _get_idf(self, term: str) -> float:
        m = self.global_term_frequency.get(term, 1.0)
        return math.log(len(self.docs) / m)


_logger = logging.getLogger(__name__)
