#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Created Date: 2020-04-16 15:45:59
# Author: Oleg Kashaev
# Contact: oleg.kashaev.4@gmail.com
# -----
# MIT License
# Copyright (c) 2020 Oleg Kashaev

import logging

from flask import Flask
from flask_restplus import Api

from easy_pyrpc.service import version
from easy_pyrpc.service import rpc_namespace

# from easy_pyrpc.service import set_custom_rpc_cache_manager
# from easy_pyrpc.service import rpc_cache
# set_custom_rpc_cache_manager(rpc_cache)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)7s %(threadName)s %(filename)s %(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

app = Flask(__name__)

api = Api(
    app,
    version=version,
    title="Sample RPC service",
    description="Sample service with RPC support",
)

api.add_namespace(rpc_namespace, path="/rpc")
