#!/usr/bin/env python3
"""
Lesson 08 starter: multi-source batching.
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
    # TODO 1: Xu ly `EOS` va `ERROR`.
    message_type = message.type
    if message_type == Gst.MessageType.EOS:
        print("Da doc het du lieu Pipeline")
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
        raise RuntimeError(f"Khong tao duoc element: {element}")
    return element


def build_source_branch(index, input_path):
    # TODO 3: Tao branch `filesrc -> h264parse -> nvv4l2decoder`.
    source = make_element("filesrc", f"file-src-{index}")
    parser = make_element("h264parse", f"h264-parser-{index}")
    decoder = make_element("nvv4l2decoder", f"hw-decoder-{index}")
    source.set_property("location", input_path)
    return source, parser, decoder

def osd_sink_pad_buffer_probe(pad, info, user_data):
    # TODO 4: In `pad_index`, `frame_num`, `objects`.
    gst_buffer = info.get_buffer()
    if not gst_buffer:
        print("Khong the lay GstBuffer")
        return Gst.PadProbeReturn.OK

    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    if not batch_meta:
        print("Khong the lay NvDsBatchMeta")
        return Gst.PadProbeReturn.OK

    l_frame = batch_meta.frame_meta_list
    while l_frame is not None:
        try:
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            break

        print(
              f"frame_num={frame_meta.frame_num} - "
              f"pad_index={frame_meta.pad_index} - "
              f"objects={frame_meta.num_obj_meta}"
        )

        try:
            l_frame = l_frame.next
        except StopIteration:
            break

    return Gst.PadProbeReturn.OK


def create_sink(platform_info):
    if platform_info.is_integrated_gpu():
        return make_element("nv3dsink", "nv3d-sink")
    if platform_info.is_platform_aarch64():
        return make_element("nv3dsink", "nv3d-sink")
    return make_element("nveglglessink", "nvvideo-renderer")


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
    platform_info = PlatformInfo()
    # TODO 5: Tao downstream elements.
    pipeline = Gst.Pipeline.new("lesson-08-pipeline")
    streammux = make_element("nvstreammux", "stream-muxer")
    pgie = make_element("nvinfer", "infer")
    tiler = make_element("nvmultistreamtiler", "multistream-tiler")
    nvvidconv = make_element("nvvideoconvert", "vidconv")
    nvosd = make_element("nvdsosd", "osd")
    sink = create_sink(platform_info)
    # TODO 6: Set property cho muxer, pgie, sink.
    streammux.set_property("batch-size", len(input_paths))
    streammux.set_property("width", 1920)
    streammux.set_property("height", 1080)
    streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)
    pgie.set_property("config-file-path", PGIE_CONFIG_PATH)
    sink.set_property("sync", False)

    tiler.set_property("rows", len(input_paths))
    tiler.set_property("columns", 1)
    tiler.set_property("width", 640)
    tiler.set_property("height", 720)

    # TODO 7: Add downstream vao pipeline.
    pipeline.add(streammux)
    pipeline.add(pgie)
    pipeline.add(tiler)
    pipeline.add(nvvidconv)
    pipeline.add(nvosd)
    pipeline.add(sink)
    # TODO 8: Lap qua tung source branch va noi vao `sink_i`.
    for index, input_path in enumerate(input_paths):
        source, parser, decoder = build_source_branch(index, input_path)
        pipeline.add(source)
        pipeline.add(parser)
        pipeline.add(decoder)
        if not source.link(parser):
            raise RuntimeError("Khong link duoc source voi parser")
        if not parser.link(decoder):
            raise RuntimeError("Khong link duoc parser voi decoder")
        
        sinkpad = streammux.request_pad_simple(f"sink_{index}")
        if not sinkpad:
            raise RuntimeError("Khong xin duoc request pad sink_{index} tu nvstreammux")

        srcpad = decoder.get_static_pad("src")
        if not srcpad:
            raise RuntimeError("Khong lay duoc src pad tu decoder")
        
        if srcpad.link(sinkpad) != Gst.PadLinkReturn.OK:
            raise RuntimeError("Khong link duoc decoder.src voi streammux.sink_{index}")

    # TODO 9: Link downstream tu muxer den sink.
    if not streammux.link(pgie):
        raise RuntimeError("Khong link duoc streammux voi pgie")
    if not pgie.link(tiler):
        raise RuntimeError("Khong link duoc pgie voi tiler")
    if not tiler.link(nvvidconv):
        raise RuntimeError("Khong link duoc tiler voi nvvidconv")
    if not nvvidconv.link(nvosd):
        raise RuntimeError("Khong link duoc nvvidconv voi nvosd")
    if not nvosd.link(sink):
        raise RuntimeError("Khong link duoc nvosd voi sink")

    # TODO 10: Gan probe vao `nvosd.sink`.
    osd_sink_pad = pgie.get_static_pad("sink")
    if not osd_sink_pad:
        raise RuntimeError("Khong lay duoc sink pad tu infer")
    osd_sink_pad.add_probe(Gst.PadProbeType.BUFFER, osd_sink_pad_buffer_probe, None)

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
