#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Created Date: 2020-04-16 15:45:59
# Author: Oleg Kashaev
# Contact: oleg.kashaev.4@gmail.com
# -----
# MIT License
# Copyright (c) 2020 Oleg Kashaev

import pickle
from cryptography.fernet import Fernet
import zipfile
import io

from .secrets import secret


def rpc_data_pack(obj):
    zipped = io.BytesIO()
    with zipfile.ZipFile(zipped, "w", zipfile.ZIP_DEFLATED, False) as zf:
        zf.writestr("rpc", pickle.dumps(obj))
    zipped.seek(0)
    return Fernet(secret).encrypt(zipped.read())


def rpc_data_unpack(data):
    zipped = io.BytesIO(Fernet(secret).decrypt(data))
    with zipfile.ZipFile(zipped, "r") as zf:
        return pickle.loads(zf.read("rpc"))
