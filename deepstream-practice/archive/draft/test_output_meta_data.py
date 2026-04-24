import os
import sys
sys.path.append(
    "/home/vtea/opt/nvidia/deepstream/deepstream-9.0/sources/deepstream_python_apps/apps"
)

import gi
gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst

import pyds

PGIE_CONFIG_PATH = "dstest1_pgie_config.txt"


def on_message(bus, message, loop):
    if message.type == Gst.MessageType.EOS:
        print("EOS: metadata probe xong.")
        loop.quit()