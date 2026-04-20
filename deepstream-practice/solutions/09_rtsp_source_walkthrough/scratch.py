#!/usr/bin/env python3
"""
Lesson 09 starter: rtsp source walkthrough.
"""

import os
import sys
from typing import Any

sys.path.append(
    "/home/vtea/opt/nvidia/deepstream/deepstream-9.0/sources/deepstream_python_apps/apps"
)

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst

import pyds

from common.platform_info import PlatformInfo

MUXER_BATCH_TIMEOUT_USEC = 33000
PGIE_CONFIG_PATH = "pgie_trafficcamnet.txt"


def on_message(bus, message, loop):
    message_type = message.type
    if message_type == Gst.MessageType.EOS:
        print("Da doc het du lieu Pipeline")
        loop.quit()
    elif message_type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(f"Error: {err}")
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
    caps = decoder_src_pad.get_current_caps()
    if not caps:
        caps = decoder_src_pad.query_caps(None)
    if not caps:
        return 
    
    caps_features = caps.get_features(0)
    if not caps_features.contains("memory:NVMM"):
        return
    
    ghost_pad = source_bin.get_static_pad("src")
    if ghost_pad and not ghost_pad.set_target(decoder_src_pad):
        print("Khong the set target cho ghost pad")


def create_source_bin(index, uri):
    bin_name = f"source-bin-{index:20d}"
    source_bin = Gst.Bin.new(bin_name)
    if not source_bin:
        raise RuntimeError("Khong the tao bin")

    uri_decode_bin = make_element("uridecodebin", f"uri-decode-bin-{index}")
    uri_decode_bin.set_property("uri", uri)
    uri_decode_bin.connect("pad-added", cb_newpad, source_bin)

    source_bin.add(uri_decode_bin)
    ghost_pad = Gst.GhostPad.new_no_target("src", Gst.PadDirection.SRC)
    if not ghost_pad:
        raise RuntimeError("Khong the tao ghost pad")

    source_bin.add_pad(ghost_pad)

    return source_bin


def create_sink(platform_info):
    if platform_info.is_platform_aarch64():
        print("GPU aarch64")
        return make_element("nv3dsink", "nv3d-sink")
    if platform_info.is_integrated_gpu():
        print("GPU integrated")
        return make_element("nv3dsink", "nv3d-sink")
    print("Using default display nveglglessink")
    return make_element("nveglglessink", "nvvideo-renderer")
    


def main(args):
    if len(args) != 2:
        print(f"usage: {args[0]} <rtsp-uri>", file=sys.stderr)
        return 1

    uri = args[1]
    if not uri:
        print("Khong co uri", file=sys.stderr)
        return 1

    platform_info = PlatformInfo()
    Gst.init(None)

    pipeline = Gst.Pipeline.new("exercise-09-pipeline")
    source_bin = create_source_bin(0, uri)
    streammux = make_element("nvstreammux", "stream-muxer")
    pgie = make_element("nvinfer", "primary-inference")
    nvvidconv = make_element("nvvideoconvert", "video-convert")
    nvosd = make_element("nvdsosd", "onscreendisplay")
    sink = create_sink(platform_info)

    streammux.set_property("batch-size", 1)
    streammux.set_property("width", 1920)
    streammux.set_property("height", 1080)
    streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)
    # streammux.set_property("live-source", True)
    pgie.set_property("config-file-path", PGIE_CONFIG_PATH)
    sink.set_property("sync", True)

    for element in (source_bin, streammux, pgie, nvvidconv, nvosd, sink):
        pipeline.add(element)

    sinkpad = streammux.request_pad_simple("sink_0")
    if not sinkpad:
        raise RuntimeError("Khong xin duoc request pad sink0 tu nvstreammux")
    
    srcpad = source_bin.get_static_pad("src")
    if not srcpad:
        raise RuntimeError("Khong lay duoc src pad tu source bin")
    
    if srcpad.link(sinkpad) != Gst.PadLinkReturn.OK:
        raise RuntimeError("Khong link duoc src pad voi sink pad")
    
    if not streammux.link(pgie):
        raise RuntimeError("Khong link duoc streammux voi infer")
    if not pgie.link(nvvidconv):
        raise RuntimeError("Khong link duoc infer voi nvvidconv")
    if not nvvidconv.link(nvosd):
        raise RuntimeError("Khong link duoc nvvidconv voi nvosd")
    if not nvosd.link(sink):
        raise RuntimeError("Khong link duoc nvosd voi sink")
    
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

