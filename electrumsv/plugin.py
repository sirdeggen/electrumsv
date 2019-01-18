#!/usr/bin/env python
#
# Electrum - lightweight Bitcoin client
# Copyright (C) 2015 Thomas Voegtlin
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from collections import namedtuple

from . import device
from .logs import logs


logger = logs.get_logger("plugin")

plugin_loaders = {}
hook_names = set()
hooks = {}

class Plugins(object):

    def __init__(self):
        self.plugins = {}

    def get(self, name):
        return self.plugins.get(name)

    def load_plugin(self, name):
        if name in self.plugins:
            return self.plugins[name]
        plugin_class = device.plugin_class(name)
        plugin = plugin_class(name)
        self.plugins[name] = plugin
        logger.debug("loaded %s", name)
        return plugin

    def create_keystore(self, d):
        device_kind = d['hw_type']
        # We want to load the plugin as a side-effect
        plugin = self.load_plugin(device_kind)
        return plugin.keystore_class(d)

    def get_plugin(self, name):
        if not name in self.plugins:
            self.load_plugin(name)
        return self.plugins[name]


def hook(func):
    hook_names.add(func.__name__)
    return func

def run_hook(name, *args):
    results = []
    f_list = hooks.get(name, [])
    for p, f in f_list:
        try:
            r = f(*args)
        except Exception:
            logger.exception("Plugin error")
            r = False
        if r:
            results.append(r)

    if results:
        assert len(results) == 1, results
        return results[0]


class BasePlugin:
    def __init__(self, name):
        self.name = name
        self.wallet = None
        # add self to hooks
        for k in dir(self):
            if k in hook_names:
                l = hooks.get(k, [])
                l.append((self, getattr(self, k)))
                hooks[k] = l

    def __str__(self):
        return self.name

    def close(self):
        # remove self from hooks
        for k in dir(self):
            if k in hook_names:
                l = hooks.get(k, [])
                l.remove((self, getattr(self, k)))
                hooks[k] = l
        self.on_close()

    def on_close(self):
        pass
