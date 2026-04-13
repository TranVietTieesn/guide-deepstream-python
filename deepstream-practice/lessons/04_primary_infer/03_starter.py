#!/usr/bin/env python3
"""
Lesson 04 starter: primary infer.

Hay doc theo thu tu:
1. `01_guide.md`
2. `02_coding_guide.md`
3. file nay
"""

import os
import sys

sys.path.append(
    "/home/vtea/opt/nvidia/deepstream/deepstream-9.0/sources/deepstream_python_apps/apps"
)

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst

from common.platform_info import PlatformInfo


MUXER_BATCH_TIMEOUT_USEC = 33000
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PGIE_CONFIG_PATH = os.path.join(PROJECT_ROOT, "dstest1_pgie_config.txt")


def on_message(bus, message, loop):
    _ = bus
    # TODO 1: Xu ly `EOS` va `ERROR`.
    _ = message
    _ = loop
    return True


def make_element(factory_name, name):
    # TODO 2: Viet helper tao element va raise `RuntimeError` neu that bai.
    _ = factory_name
    _ = name
    raise NotImplementedError("TODO: implement make_element()")


def create_sink(platform_info):
    # TODO 3: Chon sink theo `PlatformInfo`.
    _ = platform_info
    raise NotImplementedError("TODO: implement create_sink()")


def main(args):
    if len(args) != 2:
        print(f"usage: {args[0]} <path-to-h264-file>", file=sys.stderr)
        return 1

    input_path = args[1]
    if not os.path.exists(input_path):
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 1
    if not os.path.exists(PGIE_CONFIG_PATH):
        print(f"Config not found: {PGIE_CONFIG_PATH}", file=sys.stderr)
        return 1

    Gst.init(None)

    # TODO 4: Tao `PlatformInfo()`, pipeline, va cac element can thiet.
    platform_info = None
    pipeline = Gst.Pipeline.new("lesson-04-pipeline")
    source = None
    parser = None
    decoder = None
    streammux = None
    pgie = None
    nvvidconv = None
    nvosd = None
    sink = None

    if not pipeline or not source or not parser or not decoder or not streammux or not pgie or not nvvidconv or not nvosd or not sink:
        print("TODO: Tao day du element truoc.", file=sys.stderr)
        return 1

    # TODO 5: Set property cho source, streammux, va pgie.

    # TODO 6: Add tat ca element vao pipeline.

    # TODO 7: Link `filesrc -> h264parse -> nvv4l2decoder`.

    # TODO 8: Xin `sink_0` tu muxer, lay `decoder.src`, va link pad-level.

    # TODO 9: Link `streammux -> pgie -> nvvidconv -> nvosd -> sink`.

    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

    print("Running primary infer lesson...")
    print("config-file-path =", PGIE_CONFIG_PATH)
    pipeline.set_state(Gst.State.PLAYING)

    try:
        loop.run()
    except KeyboardInterrupt:
        print("Stop by user.")
    finally:
        pipeline.set_state(Gst.State.NULL)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
