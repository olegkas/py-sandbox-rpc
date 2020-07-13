#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Created Date: 2020-04-16 15:45:59
# Author: Oleg Kashaev
# Contact: oleg.kashaev.4@gmail.com
# -----
# MIT License
# Copyright (c) 2020 Oleg Kashaev

import requests
import inspect
import types
import ast
import importlib
import os.path
import logging
import hashlib
import signal
import traceback

from sandbox_rpc.common import rpc_data_pack, rpc_data_unpack, settings, RpcMockPackage, RpcFnCodeContatiner, \
    RpcRemoteException, RpcRegisterException, RpcInvokeException, RpcKeepAliveException, RpcConnectionException, \
    RpcNoRegistryWarning

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)7s %(threadName)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


__headers = {'Content-Type': 'application/octet-stream'}
__sources_cash = {}

__url = None
__keep_alive_interval = int(settings.DEFAULT_CACHE_TTL * 0.3)  # in seconds, <= 0 means do not do keep alive requests
__return_stdout = False
__return_stderr = False


def __config(service, return_stdout=False, return_stderr=False, keep_alive=True):
    global __url
    __url = service

    global __keep_alive_interval
    if not keep_alive:
        __keep_alive_interval = 0

    global __return_stdout
    __return_stdout = return_stdout

    global __return_stderr
    __return_stderr = return_stderr


def is_package(module):
    assert isinstance(module, types.ModuleType)
    if type(module.__spec__.loader) is importlib.machinery.SourceFileLoader:
        module_path = os.path.dirname(os.path.abspath(module.__spec__.origin))
        project_path = os.path.abspath(os.path.curdir)
        return os.path.commonpath([module_path, project_path]) == project_path
    return False


def fn_module_source(fn):
    fn_source = "".join(inspect.findsource(fn)[0])
    hex_digest = hashlib.new("blake2s", fn_source.encode("utf-8")).hexdigest()

    logging.debug(f"{fn.__name__}: {hex_digest}")
    logging.debug(fn_source)

    return fn_source, hex_digest


def build_fn_imports(fn, fn_source, hex_digest):
    module_imports = __sources_cash.get(hex_digest)
    if module_imports is None:
        root = ast.parse(fn_source, fn.__code__.co_filename)
        module_imports = {}
        for node in ast.iter_child_nodes(root):
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue

            for n in node.names:
                if isinstance(node, ast.ImportFrom):
                    imp = (node.module, n.name, n.asname)
                else:
                    imp = (n.name, None, n.asname)

                key = n.asname if n.asname else n.name
                module_imports[key] = imp
                logging.debug(f"IMPORT {key} => {imp}")

        logging.debug(f"module imports: {module_imports}")
        __sources_cash[hex_digest] = module_imports
    else:
        logging.debug(f"module imports (from cache): {module_imports}")

    fn_globals = dict(inspect.getmembers(fn))["__globals__"]

    fn_imports = []
    for name in fn.__code__.co_names:
        val = fn_globals.get(name)
        if isinstance(val, types.ModuleType) and not is_package(val):
            fn_imports.append(module_imports[name])

    # for i, imp in enumerate(fn_imports):
    #     logging.debug(f"build_fn_imports result {i}: {imp}")

    return fn_imports


def collect_code_names(code):
    co_names = list(code.co_names)
    for const in code.co_consts:
        if isinstance(const, types.CodeType):
            co_names.extend(collect_code_names(const))
    return co_names


def build_namespace(fn):
    fn_members = dict(inspect.getmembers(fn))
    fn_globals = fn_members["__globals__"]

    in_packages = {}
    in_globals = {}

    to_find = collect_code_names(fn.__code__)
    logging.debug(f"To find: {to_find}")
    while to_find:
        var_name = to_find.pop(0)
        if var_name in fn_globals:
            var_val = fn_globals[var_name]
            if not isinstance(var_val, types.FunctionType):
                if not isinstance(var_val, types.ModuleType):
                    in_globals[var_name] = var_val
                elif is_package(var_val):
                    in_packages[var_name] = var_val

        for k, v in list(in_packages.items()):
            if hasattr(v, var_name):
                in_packages[f"{k}.{var_name}"] = getattr(v, var_name)

    logging.debug(f"In globals: {in_globals}")
    logging.debug(f"In packages: {in_packages}")

    sorted_in_packages = sorted(in_packages.items(), key=lambda x: x[0].count("."))
    logging.debug(f"In packages (sorted): {sorted_in_packages}")

    module_mocks = {}
    for k, v in sorted_in_packages:
        if not isinstance(v, (int, float, str, list, tuple, set, dict, object, types.ModuleType)):
            continue

        path = k.split(".")
        if len(path) == 1 and isinstance(v, types.ModuleType):
            if k not in module_mocks:
                module_mocks[k] = RpcMockPackage(k)
            continue

        if len(path) > 1:
            obj_res = module_mocks[path[0]]
            for i, name in enumerate(path[1:]):
                if not hasattr(obj_res, name):
                    search_name = ".".join(path[:i + 2])
                    val = in_packages[search_name]
                    if isinstance(val, types.ModuleType):
                        val = RpcMockPackage(search_name)

                    setattr(obj_res, name, val)
                obj_res = getattr(obj_res, name)

    namespace = in_globals.copy()
    namespace.update(module_mocks)
    logging.debug(f"namespace: {namespace}")
    return namespace


def rpc(fn):
    fn_source, hex_digest = fn_module_source(fn)
    is_source_registered = hex_digest in __sources_cash

    def rpc_method_wrapper(*args, **kwargs):
        invoke_pack = rpc_data_pack({
            "args": args,
            "kwargs": kwargs,
            "namespace": build_namespace(fn),
            "settings": {
                "return_stdout": __return_stdout,
                "return_stderr": __return_stderr
            }
        })

        try:
            resp = requests.post(f"{__url}/invoke/{hex_digest}/{fn.__name__}", data=invoke_pack, headers=__headers)
            logging.debug(resp)

            if resp.status_code == 200:
                resp_data = rpc_data_unpack(resp.content)
                [print(s, end="") for s in resp_data.get("fn_output", [])]

                fn_return = resp_data["return"]
                if isinstance(fn_return, RpcRemoteException):
                    fn_return.fix_tb_code_lines(fn)
                    raise fn_return

                return fn_return
            else:
                return None
        except requests.exceptions.ConnectionError as rce:
            logging.error(f"{fn.__name__} invoke failed with error: {rce}")
            logging.debug(traceback.format_exc())
            raise RpcConnectionException(rce) from rce
        except requests.exceptions.RequestException as re:
            logging.error(f"{fn.__name__} invoke failed with error: {re}")
            raise RpcInvokeException(re) from re

    def keep_alive(signum, frame):

        try:
            ka_resp = requests.get(f"{__url}/keep-alive/{hex_digest}")
            if ka_resp.status_code == 200:
                logging.info(f"Keep-alive probe for resource {hex_digest} succeeded!")
            elif ka_resp.status_code == 404:
                msg = f"No resource {hex_digest} found"
                logging.warning(msg)
                raise RpcNoRegistryWarning(msg)
            else:
                msg = f"Error status {ka_resp.status_code} for resource {hex_digest} keep alive probe"
                logging.error(msg)
                raise RpcKeepAliveException(msg)
        except requests.exceptions.ConnectionError as rce:
            logging.error(f"{fn.__name__} keep-alive connection error: {rce}")
            logging.debug(traceback.format_exc())
            raise RpcConnectionException(rce) from rce
        except requests.exceptions.RequestException as re:
            logging.error(f"{fn.__name__} keep-alive failed with error: {re}")
            raise RpcRegisterException(re) from re

        signal.signal(signal.SIGALRM, keep_alive)
        signal.alarm(__keep_alive_interval)

    fe_imports = build_fn_imports(fn, fn_source, hex_digest)

    register_pack = rpc_data_pack({
        "imports": fe_imports,
        "code": RpcFnCodeContatiner(fn)
    })

    try:
        resp = requests.post(f"{__url}/register/{hex_digest}/{fn.__name__}", data=register_pack, headers=__headers)
        assert resp.status_code == 200
    except requests.exceptions.ConnectionError as rce:
        logging.error(f"{fn.__name__} registration failed with error: {rce}")
        raise RpcConnectionException(rce) from rce
    except requests.exceptions.RequestException as re:
        logging.error(f"{fn.__name__} registration failed with error: {re}")
        raise RpcRegisterException(re) from re

    if __keep_alive_interval > 0 and is_source_registered:
        signal.signal(signal.SIGALRM, keep_alive)
        signal.alarm(__keep_alive_interval)

    return rpc_method_wrapper


rpc.config = __config
