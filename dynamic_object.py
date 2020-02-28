# !/usr/bin/env python
# -*- coding:utf-8 -*-

from collections import namedtuple
from copy import deepcopy


class DynamicObject(object):
    """Dynamic Object"""

    def __init__(self, **attr_dict):
        self._attr_dict = attr_dict

    def __getattr__(self, name):
        return self._attr_dict[name] if name in self._attr_dict else None

    def __setattr__(self, name, value):
        if '_attr_dict' == name:
            object.__setattr__(self, name, value)
        else:
            if value is None:
                if name in self._attr_dict:
                    del self._attr_dict[name]
            else:
                self._attr_dict[name] = value

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __contains__(self, key):
        return key in self._attr_dict

    def __str__(self):
        _Class = namedtuple(self.__class__.__name__, self._attr_dict.keys())
        return str(_Class(*self._attr_dict.values()))

    __repr__ = __str__

    def __deepcopy__(self, memo):
        return DynamicObject(**self._attr_dict)

    def to_dict(self):
        return deepcopy(self._attr_dict)
