#!/usr/bin/env python3
"""
Lesson 04 starter: primary infer.

Hay doc theo thu tu:
1. `01_guide.md`
2. `02_coding_guide.md`
3. file nay
"""

from math import sin
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
PGIE_CONFIG_PATH = "dstest1_pgie_config.txt"


def on_message(bus, message, loop):
    _ = bus
    # TODO 1: Xu ly `EOS` va `ERROR`.
    message_type = message.type
    if message_type == Gst.MessageType.EOS:
        print("Da doc het pipeline du lieu")
        loop.quit()
    elif message_type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(f"ERR: {err}")
        if debug:
            print(f"DEBUG: {debug}")
        loop.quit()
    return True


def make_element(factory_name, name):
    # TODO 2: Viet helper tao element va raise `RuntimeError` neu that bai.
    element = Gst.ElementFactory.make(factory_name, name)
    if not element:
        raise RuntimeError(f"Element {factory_name} khong duoc khoi tao")
    return element


def create_sink(platform_info):
    # TODO 3: Chon sink theo `PlatformInfo`.
    if platform_info.is_integrated_gpu():
        print("GPU integrated")
        return make_element("nv3dsink", "nv3d-sink")

    if platform_info.is_platform_aarch64():
        print("GPU aarch64")
        return make_element("nv3dsink", "nv3d-sink")

    print("using default platform display nveglglessink")
    return make_element("nveglglessink", "nvvideo-renderer")


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
    platform_info = PlatformInfo()

    pipeline = Gst.Pipeline.new("lesson-04-pipeline")
    source = make_element("filesrc", "file-src")
    parser = make_element("h264parse", "parser")
    decoder = make_element("nvv4l2decoder", "decoder")
    streammux = make_element("nvstreammux", "stream-muxer")
    pgie = make_element("nvinfer", "primary-inference")
    nvvidconv = make_element("nvvideoconvert", "video-convert")
    nvosd = make_element("nvdsosd", "onscreendisplay")
    sink = create_sink(platform_info)

    # TODO 5: Set property cho source, streammux, va pgie.
    source.set_property("location", input_path)
    # sink.set_property("sync", False)
    streammux.set_property("batch-size", 1)
    streammux.set_property("width", 1920)
    streammux.set_property("height", 1080)
    streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)
    pgie.set_property("config-file-path", PGIE_CONFIG_PATH)
    # TODO 6: Add tat ca element vao pipeline.
    pipeline.add(source)
    pipeline.add(parser)
    pipeline.add(decoder)
    pipeline.add(streammux)
    pipeline.add(pgie)
    pipeline.add(nvvidconv)
    pipeline.add(nvosd)
    pipeline.add(sink)
    # TODO 7: Link `filesrc -> h264parse -> nvv4l2decoder`.
    if not source.link(parser):
        raise RuntimeError("Khong link duoc source voi parser")
    if not parser.link(decoder):
        raise RuntimeError("Khong link duoc parser voi decoder")
    # TODO 8: Xin `sink_0` tu muxer, lay `decoder.src`, va link pad-level.
    sinkpad = streammux.request_pad_simple("sink_0")
    if not sinkpad:
        raise RuntimeError("Khong xin duoc request pad sink0 tu nvstreammux")
    
    srcpad = decoder.get_static_pad("src")
    if not srcpad:
        raise RuntimeError("Khong lay duoc pad tu decoder")

    # TODO 9: Link `streammux -> pgie -> nvvidconv -> nvosd -> sink`.
    if srcpad.link(sinkpad) != Gst.PadLinkReturn.OK:
        raise RuntimeError("Khong link duoc decoder.src -> streammux.sink0")

    if not streammux.link(pgie):
        raise RuntimeError("Khong link duoc sink0 den pgie")
    
    if not pgie.link(nvvidconv):
        raise RuntimeError("Khong link duoc pgie voi nvvidconv")

    if not nvvidconv.link(nvosd):
        raise RuntimeError("Khong link duoc nvvidconv voi nviosd")
    
    if not nvosd.link(sink):
        raise RuntimeError("Khong link duoc nvosd voi sink")

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
