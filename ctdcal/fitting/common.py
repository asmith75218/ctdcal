#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:package: ctdcal.fitting.common
:file: ctdcal/fitting/common.py
:author: Allen Smith
:brief: Common code for use across ctdcal fitting modules
"""
import json

from munch import Munch


class BottleFlags(Munch):
    """
    A dictionary class with the attribute-style access of Munch, plus methods
    for adding nodes and flag data, and loading or saving to/from a JSON file.
    TODO: Move this to ctdcal.flagging.common after reorg
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_node(self, label, keys):
        """
        Add a new empty node.

        Parameters
        ----------
        label (str) - name of node
        keys (list) - names of node keys
        """
        key_dict = {k: [] for k in keys}
        node = ({label: BottleFlags(key_dict)})
        self.update(node)

    def update_node(self, **kwargs):
        for k, v in kwargs.items():
            self[k].append(v)

    def save(self, fname):
        """
        Export the flags to a JSON file.

        Pretty printing may be removed or made optional in future updates.
        """
        with open(fname, 'w') as f:
            f.write(self.toJSON(indent=4))


class NodeNotFoundError(Exception):
    pass


# Function definitions
# --------------------

# BottleFlag wrangling
# TODO: Move to ctdcal.flagging.common after reorg
def df_node_to_BottleFlags(df):
    """
    Convert a flag node from a DataFrame to a formatted BottleFlags object

    Parameters
    ----------
    df - DataFrame
    label - str

    Returns
    -------
    BottleFlags object
    """
    node_dict = df.to_dict()
    for k, v in node_dict.items():
        node_dict[k] = [vv for kk, vv in v.items()]
    return BottleFlags(node_dict)


def get_node(fname, label):
    with open(fname, 'r') as f:
        flags = json.load(f)
        if label in flags:
            return BottleFlags(flags[label])
        else:
            raise NodeNotFoundError


def save_node(fname, node, label, create_new=False):
    with open(fname, 'r') as f:
        buf = f.read()
    if buf == '':
        # File exists but is empty
        flags = BottleFlags()
    else:
        flags = BottleFlags.fromJSON(buf)
    if label in flags or create_new is True:
        flags[label] = node
    else:
        raise NodeNotFoundError("The node '%s' was not found in %s" % (label, fname))
    flags.save(fname)
