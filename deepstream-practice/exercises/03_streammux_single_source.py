#!/usr/bin/env python3
"""
Exercise 03: Single-source streammux.

Pipeline:
    filesrc -> h264parse -> nvv4l2decoder -> nvstreammux -> fakesink

Muc tieu:
- Hieu request pad cua `nvstreammux`.
- Hieu vi sao DeepStream van can mux khi chi co 1 source.

Cach chay:
    python3 exercises/03_streammux_single_source.py /path/to/sample.h264
"""

import os
import sys

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst


MUXER_BATCH_TIMEOUT_USEC = 33000


def on_message(bus, message, loop):
    if message.type == Gst.MessageType.EOS:
        print("EOS: streammux exercise xong.")
        loop.quit()
    elif message.type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(f"ERROR: {err}")
        if debug:
            print(f"DEBUG: {debug}")
        loop.quit()
    return True


def make_element(factory_name, name):
    element = Gst.ElementFactory.make(factory_name, name)
    if not element:
        raise RuntimeError(f"Khong tao duoc element: {factory_name}")
    return element


def main(args):
    if len(args) != 2:
        print(f"usage: {args[0]} <path-to-h264-file>", file=sys.stderr)
        return 1

    input_path = args[1]
    if not os.path.exists(input_path):
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 1

    Gst.init(None)

    pipeline = Gst.Pipeline.new("exercise-03-pipeline")
    source = make_element("filesrc", "file-source")
    parser = make_element("h264parse", "h264-parser")
    decoder = make_element("nvv4l2decoder", "hw-decoder")
    streammux = make_element("nvstreammux", "stream-muxer")
    sink = make_element("fakesink", "fake-sink")

    source.set_property("location", input_path)
    streammux.set_property("batch-size", 1)
    streammux.set_property("width", 1920)
    streammux.set_property("height", 1080)
    streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)
    sink.set_property("sync", False)

    for element in (source, parser, decoder, streammux, sink):
        pipeline.add(element)

    if not source.link(parser):
        raise RuntimeError("Khong link duoc filesrc -> h264parse")
    if not parser.link(decoder):
        raise RuntimeError("Khong link duoc h264parse -> nvv4l2decoder")

    sinkpad = streammux.request_pad_simple("sink_0")
    if not sinkpad:
        raise RuntimeError("Khong xin duoc request pad sink_0 tu nvstreammux")

    srcpad = decoder.get_static_pad("src")
    if not srcpad:
        raise RuntimeError("Khong lay duoc src pad tu decoder")

    if srcpad.link(sinkpad) != Gst.PadLinkReturn.OK:
        raise RuntimeError("Khong link duoc decoder.src -> streammux.sink_0")

    if not streammux.link(sink):
        raise RuntimeError("Khong link duoc nvstreammux -> fakesink")

    bus = pipeline.get_bus()
    loop = GLib.MainLoop()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

    print("Running streammux single-source exercise...")
    print("batch-size =", streammux.get_property("batch-size"))
    print("width =", streammux.get_property("width"))
    print("height =", streammux.get_property("height"))

    pipeline.set_state(Gst.State.PLAYING)

    try:
        loop.run()
    except KeyboardInterrupt:
        print("Stop by user.")
    finally:
        pipeline.set_state(Gst.State.NULL)

    # TODO: Thu doi `batch-size` thanh 2 va ghi ra ban nghi muxer se cho dieu gi.
    # TODO: Them source thu hai va xin them `sink_1`.
    # TODO: Thu doi `width`/`height` de hieu muxer dang xac dinh output frame size.
    #
    # SELF-CHECK:
    # - Tai sao `nvstreammux` dung request pad thay vi chi co 1 sink pad co dinh?
    # - Vi sao pipeline DeepStream van can mux du chi co 1 source?
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
