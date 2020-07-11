#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Created Date: 2020-04-16 15:45:59
# Author: Oleg Kashaev
# Contact: oleg.kashaev.4@gmail.com
# -----
# MIT License
# Copyright (c) 2020 Oleg Kashaev

import logging

from flask_restplus import Namespace, Resource
from flask import request, make_response
from sandbox_rpc.service import rpc_backend

rpc_namespace = Namespace(
    'PySandboxRPC',
    description='RPC handler namespace')


@rpc_namespace.route("/invoke/<string:source_hash>/<string:method_name>")
class Invoke(Resource):
    def post(self, source_hash, method_name):
        logging.info("{}: {}".format(request.method, request.url))
        data, status_code = rpc_backend.invoke(source_hash, method_name, request.get_data())
        resp = make_response(data, status_code)
        resp.headers["Content-Type"] = "application/x-binary"
        return resp


@rpc_namespace.route("/register/<string:source_hash>/<string:method_name>")
class Register(Resource):
    def post(self, source_hash, method_name):
        logging.info("{}: {}".format(request.method, request.url))
        rpc_backend.register(source_hash, method_name, request.get_data())
        data = {"source_hash": source_hash}
        resp = make_response(data, 200)
        resp.headers["Content-Type"] = "application/json"
        return resp


@rpc_namespace.route("/keep-alive/<string:source_hash>")
class KeepAlive(Resource):
    def get(self, source_hash):
        logging.info(f"{request.method}: {request.url}")
        data, status_code = rpc_backend.keep_alive(source_hash)
        resp = make_response(data, status_code)
        resp.headers["Content-Type"] = "application/json"
        return resp
