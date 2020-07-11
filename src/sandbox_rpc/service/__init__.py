#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Created Date: 2020-04-16 15:45:59
# Author: Oleg Kashaev
# Contact: oleg.kashaev.4@gmail.com
# -----
# MIT License
# Copyright (c) 2020 Oleg Kashaev

from .rpc_flask_namespace import rpc_namespace
from .rpc_backend import set_custom_rpc_cache_manager
with open("VERSION") as vf:
    version = vf.read().strip()
