#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Created Date: 2020-04-16 15:45:59
# Author: Oleg Kashaev
# Contact: oleg.kashaev.4@gmail.com
# -----
# MIT License
# Copyright (c) 2020 Oleg Kashaev

import pickle
import time
import logging

from collections import namedtuple

props = namedtuple("CacheRecordProps", "KEY DATA EXP")("key", "data", "expiration")

__cache_file_name = "rpc_cache.dat"


def __make_record(key, val, ttl=0):
    exp = None
    if isinstance(ttl, (int, float)) and ttl > 0:
        exp = time.time() + ttl

    return {
        props.KEY: key,
        props.DATA: val,
        props.EXP: exp
    }


def __cache_is_expired(cache_item):
    exp = cache_item[props.EXP]
    if isinstance(exp, float) and exp > time.time():
        return False
    return exp is not None


def __cache_remove_expired(cache_data):
    logging.debug(f"cache: remove expired cache elements")
    return {
        k: v for k, v in cache_data.items()
        if not __cache_is_expired(v)
    }


def __cache_load():
    cache_data = {}
    try:
        with open(__cache_file_name, "rb") as f:
            cache_data = pickle.loads(f.read())
    except Exception as e:
        logging.warning(f"cache: {e}")

    cache_data = __cache_remove_expired(cache_data)

    logging.debug(f"cache: loaded {len(cache_data)} cache elements")

    return cache_data


def __cache_save(cache_data):
    logging.debug(f"cache: saving {len(cache_data)} cache elements")
    try:
        with open(__cache_file_name, "wb") as f:
            f.write(pickle.dumps(cache_data))
    except Exception as e:
        logging.error(f"cache: {e}")


def cache_exists(key):
    logging.debug(f"cache: check {key} exists")
    return key in __cache_load()


def cache_get(key):
    logging.debug(f"cache: get {key}")
    return __cache_load().get(key, {}).get(props.DATA)


def cache_set(key, val, ttl=0):
    logging.debug(f"cache: set {key}, ttl: {ttl}")
    cache_data = __cache_load()
    assert key not in cache_data
    cache_data[key] = __make_record(key, val, ttl)
    cache_data = __cache_remove_expired(cache_data)
    __cache_save(cache_data)


def cache_update(key, val, ttl=0):
    logging.debug(f"cache_: pdate {key}, ttl: {ttl}")
    cache_data = __cache_load()
    assert key in cache_data
    cache_data[key] = __make_record(key, val, ttl)
    __cache_save(cache_data)
