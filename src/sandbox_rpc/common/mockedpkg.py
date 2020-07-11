#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Created Date: 2020-04-16 15:45:59
# Author: Oleg Kashaev
# Contact: oleg.kashaev.4@gmail.com
# -----
# MIT License
# Copyright (c) 2020 Oleg Kashaev

class RpcMockPackage:
    def __init__(self, name):
        self.___module_name = name

    def __repr__(self):
        attrs = {k: v for k, v in vars(self).items() if not k.startswith("_")}
        return f"<{self.__class__.__name__} for package '{self.___module_name}': {attrs}>"

