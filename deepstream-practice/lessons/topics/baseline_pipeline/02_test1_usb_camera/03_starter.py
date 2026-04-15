#!/usr/bin/env python3
"""
Lesson 02 starter: USB camera.

Pipeline muc tieu:
    v4l2src -> capsfilter -> videoconvert -> nvvideoconvert -> capsfilter ->
    nvstreammux -> nvinfer -> nvvideoconvert -> nvdsosd -> sink
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
REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")
)
PGIE_CONFIG_PATH = os.path.join(REPO_ROOT, "apps", "deepstream-test1-usbcam", "dstest1_pgie_config.txt")


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
        print(f"usage: {args[0]} <v4l2-device-path>", file=sys.stderr)
        return 1

    device_path = args[1]
    if not os.path.exists(device_path):
        print(f"Device not found: {device_path}", file=sys.stderr)
        return 1
    if not os.path.exists(PGIE_CONFIG_PATH):
        print(f"Config not found: {PGIE_CONFIG_PATH}", file=sys.stderr)
        return 1

    Gst.init(None)
    platform_info = PlatformInfo()

    pipeline = Gst.Pipeline.new("lesson-02-pipeline")
    source = None
    caps_v4l2src = None
    vidconvsrc = None
    nvvidconvsrc = None
    caps_vidconvsrc = None
    streammux = None
    pgie = None
    nvvidconv = None
    nvosd = None
    sink = None

    if not pipeline or not source or not caps_v4l2src or not vidconvsrc or not nvvidconvsrc or not caps_vidconvsrc or not streammux or not pgie or not nvvidconv or not nvosd or not sink:
        print("TODO: Tao day du element truoc.", file=sys.stderr)
        return 1

    # TODO 4: Set caps va property cho source, bridge, mux, infer, sink.

    # TODO 5: Add element vao pipeline.

    # TODO 6: Link source -> caps -> videoconvert -> nvvideoconvert -> caps.

    # TODO 7: Xin request pad tu muxer va link pad-level vao `sink_0`.
    sinkpad = None
    srcpad = None

    # TODO 8: Link downstream `streammux -> pgie -> nvvidconv -> nvosd -> sink`.

    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

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
