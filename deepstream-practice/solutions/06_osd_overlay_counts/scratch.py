#!/usr/bin/env python3
"""
Lesson 06 starter: OSD overlay counts.

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
import pyds


PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3
MUXER_BATCH_TIMEOUT_USEC = 33000
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PGIE_CONFIG_PATH = os.path.join(PROJECT_ROOT, "dstest1_pgie_config.txt")


def on_message(bus, message, loop):
    # TODO 1: Xu ly `EOS` va `ERROR`.
    message_type = message.type
    if message_type == Gst.MessageType.EOS:
        print("Da doc het du lieu pipeline")
        loop.quit()
    elif message_type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(f"ERROR: {err}")
        if debug:
            print(f"DEBUG: {debug}")
        loop.quit()
    return True


def make_element(factory_name, name):
    # TODO 2: Viet helper tao element.
    element = Gst.ElementFactory.make(factory_name, name)
    if not element:
        raise RuntimeError(f"Khong tao duoc element: {factory_name}")
    return element


def create_sink(platform_info):
    # TODO 3: Chon sink theo `PlatformInfo`.
    if platform_info.is_integrated_gpu():
        print("GPU integrated")
        return make_element("nv3dsink", "nv3d-sink")
    
    if platform_info.is_platform_aarch64():
        print("GPU arrch64")
        return make_element("nv3dsink", "nv3d-sink")
    
    print("Using default display nveglglessink")
    return make_element("nveglglessink", "nvvideo-renderer")


def colorize_object(obj_meta):
    # TODO 4: Doi mau bbox theo `class_id`.
    _ = obj_meta


def osd_sink_pad_buffer_probe(pad, info, user_data):
    # TODO 5: Dem object, doi mau bbox, tao text overlay bang `NvDsDisplayMeta`.
    _ = pad
    _ = info
    _ = user_data
    return Gst.PadProbeReturn.OK


def main(args):
    if len(args) != 2:
        print(f"usage: {args[0]} <path-to-h264-file>", file=sys.stderr)
        return 1

    input_path = args[1]
    if not os.path.exists(input_path):
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 1

    Gst.init(None)

    # TODO 6: Tao pipeline va cac element.
    platform_info = None
    pipeline = Gst.Pipeline.new("lesson-06-pipeline")
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

    # TODO 7: Set property cho source, muxer, pgie.
    # TODO 8: Add element vao pipeline.
    # TODO 9: Link den decoder.
    # TODO 10: Link vao `nvstreammux.sink_0`.
    # TODO 11: Link downstream tu muxer den sink.

    # TODO 12: Gan probe vao `nvosd.sink`.

    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

    print("Running overlay lesson...")
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
