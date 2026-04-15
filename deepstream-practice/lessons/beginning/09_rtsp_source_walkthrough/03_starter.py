#!/usr/bin/env python3
"""
Lesson 09 starter: RTSP source walkthrough.
"""

import os
import sys

sys.path.append(
    "/home/vtea/opt/nvidia/deepstream/deepstream-9.0/sources/deepstream_python_apps/apps"
)

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst


MUXER_BATCH_TIMEOUT_USEC = 33000
PGIE_CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "archive", "exercises", "07_config_variants", "pgie_trafficcamnet.txt")
)


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


def cb_newpad(decodebin, decoder_src_pad, source_bin):
    # TODO 3: Lay caps, check NVMM, va noi ghost pad vao `decoder_src_pad`.
    _ = decodebin
    _ = decoder_src_pad
    _ = source_bin


def create_source_bin(index, uri):
    # TODO 4: Tao source bin + uridecodebin + ghost pad.
    _ = index
    _ = uri
    raise NotImplementedError("TODO: implement create_source_bin()")


def main(args):
    if len(args) != 2:
        print(f"usage: {args[0]} <rtsp-uri>", file=sys.stderr)
        return 1

    uri = args[1]
    if not uri.startswith("rtsp://"):
        print("Bai nay cho RTSP URI, vi du rtsp://...", file=sys.stderr)
        return 1

    Gst.init(None)

    # TODO 5: Tao source bin va downstream elements.
    pipeline = Gst.Pipeline.new("lesson-09-pipeline")
    source_bin = None
    streammux = None
    pgie = None
    nvvidconv = None
    nvosd = None
    sink = None

    if not pipeline or not source_bin or not streammux or not pgie or not nvvidconv or not nvosd or not sink:
        print("TODO: Tao day du elements truoc.", file=sys.stderr)
        return 1

    # TODO 6: Set property cho muxer, pgie, sink. Nho `live-source=True`.
    # TODO 7: Add tat ca vao pipeline.
    # TODO 8: Xin `sink_0`, lay `source_bin.src`, va link vao muxer.
    # TODO 9: Link downstream tu muxer den sink.

    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

    print("Running RTSP walkthrough lesson...")
    print("URI =", uri)
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
