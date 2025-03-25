"""
Persistence module for the crawler system.
Handles data storage across different storage backends.
"""

from .data_persistence_manager import DataPersistenceManager
from .mongodb_handler import MongoDBHandler
from .notion_handler import NotionHandler
from .local_storage import LocalStorage

__all__ = [
    'DataPersistenceManager',
    'MongoDBHandler',
    'NotionHandler',
    'LocalStorage'
]
