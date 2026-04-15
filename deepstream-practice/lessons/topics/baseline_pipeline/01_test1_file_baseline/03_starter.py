#!/usr/bin/env python3
"""
Lesson 01 starter: file baseline.

Pipeline muc tieu:
    filesrc -> h264parse -> nvv4l2decoder -> nvstreammux -> nvinfer ->
    nvvideoconvert -> nvdsosd -> sink

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

import pyds

from common.platform_info import PlatformInfo


MUXER_BATCH_TIMEOUT_USEC = 33000
REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")
)
PGIE_CONFIG_PATH = os.path.join(REPO_ROOT, "apps", "deepstream-test1", "dstest1_pgie_config.txt")


def osd_sink_pad_buffer_probe(pad, info, u_data):
    # TODO 0: Doc metadata tu buffer sau khi `nvinfer` da attach object meta.
    _ = pad
    _ = info
    _ = u_data
    return Gst.PadProbeReturn.OK


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
    # TODO 3: Chon sink theo platform.
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
    platform_info = PlatformInfo()

    # TODO 4: Tao pipeline va cac element can thiet.
    # Giong sample goc, lesson nay di theo chuoi:
    # filesrc -> h264parse -> nvv4l2decoder -> nvstreammux -> nvinfer ->
    # nvvideoconvert -> nvdsosd -> sink
    pipeline = Gst.Pipeline.new("lesson-01-pipeline")
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

    # TODO 5: Set property cho source, mux, infer, va sink.
    # - source.location = input_path
    # - streammux.batch-size = 1
    # - streammux.width/height/batched-push-timeout
    # - pgie.config-file-path = PGIE_CONFIG_PATH
    # - sink.sync = False

    # TODO 6: Add tat ca element vao pipeline.
    # TODO 7: Link `filesrc -> h264parse -> nvv4l2decoder`.
    # TODO 8: Xin `sink_0` tu muxer va lay `decoder.src`.
    # TODO 9: Link pad-level va downstream chain.
    # TODO 10: Gan pad probe vao sink pad cua `nvdsosd`.

    sinkpad = None
    srcpad = None

    # TODO 11: Tao bus watch va `GLib.MainLoop()`.
    # TODO 12: Dua pipeline sang `PLAYING`.

    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

    try:
        _ = pyds  # keep import visible for lesson readers
        loop.run()
    except KeyboardInterrupt:
        print("Stop by user.")
    finally:
        pipeline.set_state(Gst.State.NULL)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
