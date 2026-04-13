#!/usr/bin/env python3
"""
Lesson 08 starter: multi-source batching.
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
PGIE_CONFIG_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "exercises", "07_config_variants", "pgie_trafficcamnet.txt"
))


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


def build_source_branch(index, input_path):
    # TODO 3: Tao branch `filesrc -> h264parse -> nvv4l2decoder`.
    _ = index
    _ = input_path
    raise NotImplementedError("TODO: implement build_source_branch()")


def osd_sink_pad_buffer_probe(pad, info, user_data):
    # TODO 4: In `pad_index`, `frame_num`, `objects`.
    _ = pad
    _ = info
    _ = user_data
    return Gst.PadProbeReturn.OK


def main(args):
    if len(args) != 3:
        print(f"usage: {args[0]} <path-a.h264> <path-b.h264>", file=sys.stderr)
        return 1

    input_paths = args[1:]
    for input_path in input_paths:
        if not os.path.exists(input_path):
            print(f"Input not found: {input_path}", file=sys.stderr)
            return 1

    Gst.init(None)

    # TODO 5: Tao downstream elements.
    pipeline = Gst.Pipeline.new("lesson-08-pipeline")
    streammux = None
    pgie = None
    nvvidconv = None
    nvosd = None
    sink = None

    if not pipeline or not streammux or not pgie or not nvvidconv or not nvosd or not sink:
        print("TODO: Tao downstream elements truoc.", file=sys.stderr)
        return 1

    # TODO 6: Set property cho muxer, pgie, sink.
    # TODO 7: Add downstream vao pipeline.
    # TODO 8: Lap qua tung source branch va noi vao `sink_i`.
    # TODO 9: Link downstream tu muxer den sink.
    # TODO 10: Gan probe vao `nvosd.sink`.

    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

    print("Running multi-source batching lesson...")
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
