#!/usr/bin/env python3
"""
Lesson 05 starter: probe batch meta.

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
    # TODO 2: Viet helper tao element.
    _ = factory_name
    _ = name
    raise NotImplementedError("TODO: implement make_element()")


def osd_sink_pad_buffer_probe(pad, info, user_data):
    # TODO 3: Doc `gst_buffer`, `batch_meta`, `frame_meta`, `obj_meta` va in thong tin.
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

    # TODO 4: Tao pipeline va cac element.
    pipeline = Gst.Pipeline.new("lesson-05-pipeline")
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

    # TODO 5: Set property cho source, streammux, pgie, sink.
    # TODO 6: Add element vao pipeline.
    # TODO 7: Link den decoder.
    # TODO 8: Link vao `nvstreammux.sink_0`.
    # TODO 9: Link downstream tu muxer den sink.

    # TODO 10: Lay `nvosd.sink` va gan probe vao do.

    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

    print("Running metadata probe lesson...")
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
