#!/usr/bin/env python3
"""
Lesson 08 starter: multi-source batching.
"""

import os
import sys
from typing import Any

sys.path.append(
    "/home/vtea/opt/nvidia/deepstream/deepstream-9.0/sources/deepstream_python_apps/apps"
)

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst

import pyds

from common.platform_info import PlatformInfo

MUXER_BATCH_TIMEOUT_USEC = 33000
PGIE_CONFIG_PATH = "pgie_trafficcamnet.txt"


def on_message(bus, message, loop):
    message_type = message.type
    if message_type == Gst.MessageType.EOS:
        print("Da doc het du lieu Pipeline")