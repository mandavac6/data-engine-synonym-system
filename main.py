import json
import os
from contextlib import asynccontextmanager
from typing import Dict, Union, List

import redis
from cachetools import LRUCache
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from db import create_db_and_tables, SessionDep
from models import Word

cache = LRUCache(maxsize=os.getenv('LRU_CACHE_SIZE', 10))

# start a Redis client
r = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=int(os.getenv('REDIS_PORT', 6379)), db=0)
ttl = int(os.getenv('TTL', 60))
use_redis_cache = os.getenv('USE_REDIS_CACHE', 'True') == 'True'
use_lru_cache = os.getenv('USE_LRU_CACHE', 'True') == 'True'


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    load_dotenv(dotenv_path='/.env')
    yield


app = FastAPI(lifespan=lifespan)


# class CacheItem:
#     def __init__(self, synonym: SynonymModel, cache_flag: bool):
#         self.synonym = synonym
#         self.cache_flag = cache_flag

class CacheItem:
    def __init__(self, synonym: List[str], cache_flag: bool):
        self.synonym = synonym
        self.cache_flag = cache_flag


@app.get("/synonym/{word}")
async def get_synonyms(word: str, session: SessionDep) -> Dict[
    str, Union[Dict[str, List], Dict[str, Union[str, bool]]]]:
    word: str = word.strip().lower()

    if use_lru_cache:
        cached_item = cache.get(word)
        if cached_item:
            return {"data": {word: cached_item.synonym}, 'meta_data': {'cache_flag': True, 'cache': 'LRUCache'}}

    if use_redis_cache:
        synonyms = r.get(word)
        if synonyms:
            return {"data": {word: json.loads(synonyms)}, 'meta_data': {'cache_flag': True, 'cache': 'Redis'}}

    synonyms = Word.get_synonyms(session=session, word_text=word)

    if not synonyms:
        raise HTTPException(status_code=404, detail=f"Synonym not found for {word}")

    if use_lru_cache:
        cache[word] = CacheItem(synonyms, False)

    if use_redis_cache:
        await r.set(word, json.dumps(synonyms), ex=ttl)

    return {"data": {word: synonyms}, 'meta_data': {"cache_flag": False}}

# @app.get("/synonym/{word}")
# async def say_hello(word: str, session: SessionDep) -> Dict[str, Union[SynonymModel, Dict[str, Union[str, bool]]]]:
#     word: str = word.strip().lower()
#
#     logger.debug(f"USE_REDIS_CACHE: {os.getenv('USE_REDIS_CACHE')}")
#
#     if use_lru_cache:
#         cached_item = cache.get(word)
#         if cached_item:
#             return {"data": cached_item.synonym, 'meta_data': {"cache_flag": True, 'cache': 'LRUCache'}}
#
#     if use_redis_cache:
#         cached_item = r.get(word)
#         if cached_item:
#             synonym = SynonymModel.model_validate_json(cached_item)
#             return {"data": synonym, 'meta_data': {"cache_flag": True, 'cache': 'Redis'}}
#
#     synonym = session.query(SynonymModel).filter(SynonymModel.word == word).first()
#
#     if not synonym:
#         raise HTTPException(status_code=404, detail=f"Synonym not found for {word}")
#
#     if use_lru_cache:
#         cache[word] = CacheItem(synonym, False)
#
#     if use_redis_cache:
#         r.set(word, synonym.json(), ex=ttl)
#
#     return {"data": synonym, 'meta_data': {"cache_flag": False}}
