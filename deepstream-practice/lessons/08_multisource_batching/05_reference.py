#!/usr/bin/env python3
"""
Lesson 08 reference: multi-source batching.
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
PGIE_CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "exercises", "07_config_variants", "pgie_trafficcamnet.txt")
)


def on_message(bus, message, loop):
    _ = bus
    if message.type == Gst.MessageType.EOS:
        print("EOS: multi-source batching xong.")
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


def build_source_branch(index, input_path):
    source = make_element("filesrc", f"file-source-{index}")
    parser = make_element("h264parse", f"h264-parser-{index}")
    decoder = make_element("nvv4l2decoder", f"hw-decoder-{index}")
    source.set_property("location", input_path)
    return source, parser, decoder


def osd_sink_pad_buffer_probe(pad, info, user_data):
    _ = pad
    _ = user_data
    gst_buffer = info.get_buffer()
    if not gst_buffer:
        return Gst.PadProbeReturn.OK

    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    l_frame = batch_meta.frame_meta_list
    while l_frame is not None:
        try:
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            break
        print(
            f"pad_index={frame_meta.pad_index} "
            f"frame_num={frame_meta.frame_num} "
            f"objects={frame_meta.num_obj_meta}"
        )
        try:
            l_frame = l_frame.next
        except StopIteration:
            break
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

    pipeline = Gst.Pipeline.new("lesson-08-pipeline")
    streammux = make_element("nvstreammux", "stream-muxer")
    pgie = make_element("nvinfer", "primary-inference")
    nvvidconv = make_element("nvvideoconvert", "video-convert")
    nvosd = make_element("nvdsosd", "onscreendisplay")
    sink = make_element("fakesink", "fake-sink")

    streammux.set_property("batch-size", len(input_paths))
    streammux.set_property("width", 1920)
    streammux.set_property("height", 1080)
    streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)
    pgie.set_property("config-file-path", PGIE_CONFIG_PATH)
    sink.set_property("sync", False)

    for element in (streammux, pgie, nvvidconv, nvosd, sink):
        pipeline.add(element)

    for index, input_path in enumerate(input_paths):
        source, parser, decoder = build_source_branch(index, input_path)
        for element in (source, parser, decoder):
            pipeline.add(element)

        if not source.link(parser):
            raise RuntimeError(f"Khong link duoc source {index} -> parser")
        if not parser.link(decoder):
            raise RuntimeError(f"Khong link duoc parser {index} -> decoder")

        sinkpad = streammux.request_pad_simple(f"sink_{index}")
        srcpad = decoder.get_static_pad("src")
        if not sinkpad or not srcpad:
            raise RuntimeError(f"Khong lay duoc pad cho source {index}")
        if srcpad.link(sinkpad) != Gst.PadLinkReturn.OK:
            raise RuntimeError(f"Khong link duoc decoder {index} vao nvstreammux")

    for upstream, downstream, label in (
        (streammux, pgie, "nvstreammux -> nvinfer"),
        (pgie, nvvidconv, "nvinfer -> nvvideoconvert"),
        (nvvidconv, nvosd, "nvvideoconvert -> nvdsosd"),
        (nvosd, sink, "nvdsosd -> fakesink"),
    ):
        if not upstream.link(downstream):
            raise RuntimeError(f"Khong link duoc {label}")

    osd_sink_pad = nvosd.get_static_pad("sink")
    if not osd_sink_pad:
        raise RuntimeError("Khong lay duoc nvosd sink pad")
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
