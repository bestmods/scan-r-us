__title__ = "Database"
__version__ = "1.0.0"

from .connection import init, setup, close, getTableSize
from .query.source import AddSource, GetSource, GetSources, UpdateSource, DeleteSource
from .query.query import AddQuery, GetQuery, GetQueries, UpdateQuery, UpdateQueryQuery, DeleteQuery