#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Created Date: 2020-04-16 15:45:59
# Author: Oleg Kashaev
# Contact: oleg.kashaev.4@gmail.com
# -----
# MIT License
# Copyright (c) 2020 Oleg Kashaev

import types
import logging


class RpcFnCodeContatiner:
    def __init__(self, fn):
        self.code_descriptor = self.__from_code(fn)

    @classmethod
    def __replace_code(cls, seq):
        new_seq = []
        for const in seq:
            if isinstance(const, types.CodeType):
                new_seq.append(cls(const))
            else:
                new_seq.append(const)
        return type(seq)(new_seq)

    @classmethod
    def __replace_code_container(cls, seq):
        new_seq = []
        for item in seq:
            if isinstance(item, RpcFnCodeContatiner):
                new_seq.append(item.code)
            else:
                new_seq.append(item)
        return type(seq)(new_seq)

    @classmethod
    def __from_code(cls, fn):
        assert isinstance(fn, (types.CodeType, types.FunctionType))
        code = fn.__code__ if isinstance(fn, types.FunctionType) else fn

        code_descriptor = {
            "argcount": code.co_argcount,
            "posonlyargcount": code.co_posonlyargcount,
            "kwonlyargcount": code.co_kwonlyargcount,
            "nlocals": code.co_nlocals,
            "stacksize": code.co_stacksize,
            "flags": code.co_flags,
            "codestring": code.co_code,
            "constants": cls.__replace_code(code.co_consts),
            "names": code.co_names,
            "varnames": code.co_varnames,
            "filename": code.co_filename,
            "name": code.co_name,
            "firstlineno": code.co_firstlineno,
            "lnotab": code.co_lnotab,
            "freevars": code.co_freevars,
            "cellvars": code.co_cellvars
        }

        logging.debug(str(code_descriptor))
        return code_descriptor

    @property
    def code(self):

        return types.CodeType(
            self.code_descriptor["argcount"],
            self.code_descriptor["posonlyargcount"],
            self.code_descriptor["kwonlyargcount"],
            self.code_descriptor["nlocals"],
            self.code_descriptor["stacksize"],
            self.code_descriptor["flags"],
            self.code_descriptor["codestring"],
            self.__replace_code_container(self.code_descriptor["constants"]),
            self.code_descriptor["names"],
            self.code_descriptor["varnames"],
            self.code_descriptor["filename"],
            self.code_descriptor["name"],
            self.code_descriptor["firstlineno"],
            self.code_descriptor["lnotab"],
            self.code_descriptor["freevars"],
            self.code_descriptor["cellvars"]
        )

    def make_fn(self, namespace, co_name=None):
        code = self.code
        if not co_name:
            co_name = code.co_name
        return types.FunctionType(code, namespace, co_name)
