#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Created Date: 2020-04-16 15:45:59
# Author: Oleg Kashaev
# Contact: oleg.kashaev.4@gmail.com
# -----
# MIT License
# Copyright (c) 2020 Oleg Kashaev

import traceback
import inspect
from requests.exceptions import ConnectionError


class RpcBaseWarning(Warning):
    def print_traceback(self):
        traceback.print_tb(self.__traceback__)


class RpcNoRegistryWarning(ResourceWarning, RpcBaseWarning):
    pass


class RpcBaseException(Exception):
    def print_traceback(self):
        traceback.print_tb(self.__traceback__)


class RpcConnectionException(ConnectionError, RpcBaseException):
    pass


class RpcRegisterException(RpcBaseException):
    pass


class RpcInvokeException(RpcBaseException):
    pass


class RpcKeepAliveException(RpcBaseException):
    pass


class RpcRemoteException(RpcBaseException):
    def __init__(self, source_ex):
        self.source_ex = source_ex
        self.source_tb = traceback.extract_tb(source_ex.__traceback__)

    def fix_tb_code_lines(self, fn):
        fn_source = inspect.findsource(fn)[0]

        for pos in range(len(self.source_tb)):
            fs = self.source_tb[pos]
            if fs.filename == fn.__code__.co_filename:
                line = fn_source[fs.lineno - 1].strip()
                self.source_tb[pos] = traceback.FrameSummary(fs.filename, fs.lineno, fs.name, line=line)

    def print_traceback(self):
        tb = traceback.extract_tb(self.__traceback__)[:-1] if self.__traceback__ else []
        tb += self.source_tb[1:]

        print('Traceback (most recent call last):')
        for sf in tb:
            print(f'  File "{sf.filename}", line {sf.lineno}, in {sf.name}')
            print(f'    {sf.line}')
        print(self)

    def __str__(self):
        return f'{self.__class__.__name__} => {self.source_ex.__class__.__name__}: {str(self.source_ex)}'
