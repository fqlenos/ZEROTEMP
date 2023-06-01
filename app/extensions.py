from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db:SQLAlchemy = SQLAlchemy()

cache = Cache(config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 60,
    'CACHE_THRESHOLD': 1000
})

limiter = Limiter(key_func=get_remote_address)