#!/usr/bin/env python3
"""
Lesson 09 reference: RTSP source walkthrough.
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
    os.path.join(os.path.dirname(__file__), "..", "..", "exercises", "07_config_variants", "pgie_trafficcamnet.txt")
)


def on_message(bus, message, loop):
    _ = bus
    if message.type == Gst.MessageType.EOS:
        print("EOS: RTSP walkthrough xong.")
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


def cb_newpad(decodebin, decoder_src_pad, source_bin):
    _ = decodebin
    caps = decoder_src_pad.get_current_caps()
    if not caps:
        caps = decoder_src_pad.query_caps(None)
    if not caps:
        print("Khong lay duoc caps tu decodebin.")
        return

    caps_features = caps.get_features(0)
    if not caps_features.contains("memory:NVMM"):
        print("Bo qua pad khong dung NVMM, can xem lai source / decode path.")
        return

    ghost_pad = source_bin.get_static_pad("src")
    if ghost_pad and not ghost_pad.set_target(decoder_src_pad):
        print("Khong gan duoc ghost pad target.")


def create_source_bin(index, uri):
    bin_name = f"source-bin-{index:02d}"
    source_bin = Gst.Bin.new(bin_name)
    if not source_bin:
        raise RuntimeError("Khong tao duoc source bin")

    uri_decode_bin = make_element("uridecodebin", f"uri-decode-bin-{index}")
    uri_decode_bin.set_property("uri", uri)
    uri_decode_bin.connect("pad-added", cb_newpad, source_bin)

    source_bin.add(uri_decode_bin)
    ghost_pad = Gst.GhostPad.new_no_target("src", Gst.PadDirection.SRC)
    if not ghost_pad:
        raise RuntimeError("Khong tao duoc ghost pad cho source bin")
    source_bin.add_pad(ghost_pad)

    return source_bin


def main(args):
    if len(args) != 2:
        print(f"usage: {args[0]} <rtsp-uri>", file=sys.stderr)
        return 1

    uri = args[1]
    if not uri.startswith("rtsp://"):
        print("Bai nay cho RTSP URI, vi du rtsp://...", file=sys.stderr)
        return 1

    Gst.init(None)

    pipeline = Gst.Pipeline.new("lesson-09-pipeline")
    source_bin = create_source_bin(0, uri)
    streammux = make_element("nvstreammux", "stream-muxer")
    pgie = make_element("nvinfer", "primary-inference")
    nvvidconv = make_element("nvvideoconvert", "video-convert")
    nvosd = make_element("nvdsosd", "onscreendisplay")
    sink = make_element("fakesink", "fake-sink")

    streammux.set_property("batch-size", 1)
    streammux.set_property("width", 1920)
    streammux.set_property("height", 1080)
    streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)
    streammux.set_property("live-source", True)
    pgie.set_property("config-file-path", PGIE_CONFIG_PATH)
    sink.set_property("sync", False)

    for element in (source_bin, streammux, pgie, nvvidconv, nvosd, sink):
        pipeline.add(element)

    sinkpad = streammux.request_pad_simple("sink_0")
    srcpad = source_bin.get_static_pad("src")
    if not sinkpad or not srcpad:
        raise RuntimeError("Khong lay duoc pad de noi source bin vao nvstreammux")
    if srcpad.link(sinkpad) != Gst.PadLinkReturn.OK:
        raise RuntimeError("Khong link duoc source bin -> nvstreammux.sink_0")

    for upstream, downstream, label in (
        (streammux, pgie, "nvstreammux -> nvinfer"),
        (pgie, nvvidconv, "nvinfer -> nvvideoconvert"),
        (nvvidconv, nvosd, "nvvideoconvert -> nvdsosd"),
        (nvosd, sink, "nvdsosd -> fakesink"),
    ):
        if not upstream.link(downstream):
            raise RuntimeError(f"Khong link duoc {label}")

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
