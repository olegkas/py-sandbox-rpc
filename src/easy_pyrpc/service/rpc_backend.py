#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Created Date: 2020-04-16 15:45:59
# Author: Oleg Kashaev
# Contact: oleg.kashaev.4@gmail.com
# -----
# MIT License
# Copyright (c) 2020 Oleg Kashaev

import logging
import importlib
import pickle
import sys
import io

from flask_restplus import Namespace
from flask import request

from easy_pyrpc.common import rpc_data_unpack, rpc_data_pack, settings, RpcRemoteException

try:
    import uwsgi as cache_man
except ModuleNotFoundError:
    import easy_pyrpc.service.rpc_cache as cache_man


def set_custom_rpc_cache_manager(custom_cache_man):
    global cache_man
    cache_man = custom_cache_man


ns = Namespace(
    'EasyPyRPC',
    description='RPC handler namespace')


def build_namespace(fn_imports, namespace):
    fn_globals = globals().copy()
    for mdl, sub, asname in fn_imports:
        _temp = importlib.__import__(mdl, fn_globals, locals(), sub)
        if sub:
            sub_name = asname if asname else sub[0]
            fn_globals[sub_name] = getattr(_temp, sub[0])
        elif asname:
            ref = _temp
            for name in mdl.split(".")[1:]:
                ref = getattr(ref, name)
            fn_globals[asname] = ref
        else:
            fn_globals[mdl.split(".")[0]] = _temp

    fn_globals.update(namespace)
    return fn_globals


def invoke(source_hash, method_name, packed_data):
    data = rpc_data_unpack(packed_data)
    logging.debug(str(data))

    args = data["args"]
    kwargs = data["kwargs"]
    namespace = data["namespace"]
    settings = data["settings"]

    logging.debug(f"args: {args}")
    logging.debug(f"kwargs: {kwargs}")
    logging.debug(f"namespace: {namespace}", )

    if not cache_man.cache_exists(source_hash):
        return {"error": source_hash}, 404

    reg_dump = pickle.loads(cache_man.cache_get(source_hash))
    if method_name not in reg_dump:
        return {"error": f"{source_hash}/{method_name}"}, 404

    fn_globals = build_namespace(reg_dump[method_name]["imports"], namespace)
    fn = reg_dump[method_name]["code"].make_fn(fn_globals)

    result = None

    std_stream_subst = io.StringIO()
    if settings.get("return_stdout"):
        sys.stdout = std_stream_subst
    if settings.get("return_stderr"):
        sys.stderr = std_stream_subst

    try:
        result = fn(*args, **kwargs)
    except Exception as e:
        logging.warning(f"Method {method_name} failed with exception {e.__class__.__name__}:")
        result = RpcRemoteException(e)
    except SystemExit as se:
        result = se.code
    finally:
        if settings.get("return_stdout") or settings.get("return_stderr"):
            if settings.get("return_stdout"):
                sys.stdout = sys.__stdout__
            if settings.get("return_stderr"):
                sys.stdout = sys.__stderr__

            std_stream_subst.seek(0)
            fn_std_all = std_stream_subst.readlines()
        else:
            fn_std_all = []

    return rpc_data_pack({
        "return": result,
        "fn_output": fn_std_all
    }), 200


def register(source_hash, method_name, packed_data):
    logging.info("{}: {}".format(request.method, request.url))
    data = rpc_data_unpack(request.get_data())
    logging.debug(str(data))

    fn_data = {
        method_name: data
    }

    if cache_man.cache_exists(source_hash):
        reg_dump = pickle.loads(cache_man.cache_get(source_hash))
        reg_dump.update(fn_data)
        cache_man.cache_update(source_hash, pickle.dumps(reg_dump), settings.DEFAULT_CACHE_TTL)
    else:
        cache_man.cache_set(source_hash, pickle.dumps(fn_data), settings.DEFAULT_CACHE_TTL)


def keep_alive(source_hash):
    data = {"source_hash": source_hash}

    reg_dump = cache_man.cache_get(source_hash)
    if reg_dump:
        cache_man.cache_update(source_hash, reg_dump, settings.DEFAULT_CACHE_TTL)
        return data, 200

    return data, 404
