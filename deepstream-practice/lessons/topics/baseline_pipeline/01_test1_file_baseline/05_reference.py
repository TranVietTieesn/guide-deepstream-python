#!/usr/bin/env python3
"""
Lesson 01 reference: file baseline.
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

from common.bus_call import bus_call
from common.platform_info import PlatformInfo


MUXER_BATCH_TIMEOUT_USEC = 33000
REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")
)
PGIE_CONFIG_PATH = os.path.join(REPO_ROOT, "apps", "deepstream-test1", "dstest1_pgie_config.txt")


def osd_sink_pad_buffer_probe(pad, info, u_data):
    frame_number = 0
    obj_counter = {
        0: 0,
        1: 0,
        2: 0,
        3: 0,
    }
    num_rects = 0

    gst_buffer = info.get_buffer()
    if not gst_buffer:
        print("Unable to get GstBuffer ")
        return Gst.PadProbeReturn.OK

    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    l_frame = batch_meta.frame_meta_list
    while l_frame is not None:
        try:
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            break

        frame_number = frame_meta.frame_num
        num_rects = frame_meta.num_obj_meta
        l_obj = frame_meta.obj_meta_list
        while l_obj is not None:
            try:
                obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
            except StopIteration:
                break
            obj_counter[obj_meta.class_id] += 1
            try:
                l_obj = l_obj.next
            except StopIteration:
                break

        display_meta = pyds.nvds_acquire_display_meta_from_pool(batch_meta)
        display_meta.num_labels = 1
        py_nvosd_text_params = display_meta.text_params[0]
        py_nvosd_text_params.display_text = (
            "Frame Number={} Number of Objects={} Vehicle_count={} Person_count={}".format(
                frame_number,
                num_rects,
                obj_counter[0],
                obj_counter[2],
            )
        )
        py_nvosd_text_params.x_offset = 10
        py_nvosd_text_params.y_offset = 12
        py_nvosd_text_params.font_params.font_name = "Serif"
        py_nvosd_text_params.font_params.font_size = 10
        py_nvosd_text_params.font_params.font_color.set(1.0, 1.0, 1.0, 1.0)
        py_nvosd_text_params.set_bg_clr = 1
        py_nvosd_text_params.text_bg_clr.set(0.0, 0.0, 0.0, 1.0)
        pyds.nvds_add_display_meta_to_frame(frame_meta, display_meta)
        try:
            l_frame = l_frame.next
        except StopIteration:
            break

    return Gst.PadProbeReturn.OK


def on_message(bus, message, loop):
    return bus_call(bus, message, loop)


def make_element(factory_name, name):
    element = Gst.ElementFactory.make(factory_name, name)
    if not element:
        raise RuntimeError(f"Khong tao duoc element: {factory_name}")
    return element


def create_sink(platform_info):
    if platform_info.is_integrated_gpu():
        return make_element("nv3dsink", "video-output")
    if platform_info.is_platform_aarch64():
        return make_element("nv3dsink", "video-output")
    return make_element("nveglglessink", "video-output")


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
    platform_info = PlatformInfo()

    pipeline = Gst.Pipeline.new("lesson-01-pipeline")
    source = make_element("filesrc", "file-source")
    parser = make_element("h264parse", "h264-parser")
    decoder = make_element("nvv4l2decoder", "hw-decoder")
    streammux = make_element("nvstreammux", "stream-muxer")
    pgie = make_element("nvinfer", "primary-inference")
    nvvidconv = make_element("nvvideoconvert", "video-convert")
    nvosd = make_element("nvdsosd", "onscreendisplay")
    sink = create_sink(platform_info)

    source.set_property("location", input_path)
    streammux.set_property("batch-size", 1)
    pgie.set_property("config-file-path", PGIE_CONFIG_PATH)
    sink.set_property("sync", False)

    if os.environ.get("USE_NEW_NVSTREAMMUX") != "yes":
        streammux.set_property("width", 1920)
        streammux.set_property("height", 1080)
        streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)

    for element in (source, parser, decoder, streammux, pgie, nvvidconv, nvosd, sink):
        pipeline.add(element)

    if not source.link(parser):
        raise RuntimeError("Khong link duoc filesrc -> h264parse")
    if not parser.link(decoder):
        raise RuntimeError("Khong link duoc h264parse -> nvv4l2decoder")

    sinkpad = streammux.request_pad_simple("sink_0")
    srcpad = decoder.get_static_pad("src")
    if not sinkpad or not srcpad:
        raise RuntimeError("Khong lay duoc pad de noi vao nvstreammux")
    if srcpad.link(sinkpad) != Gst.PadLinkReturn.OK:
        raise RuntimeError("Khong link duoc decoder.src -> streammux.sink_0")

    if not streammux.link(pgie):
        raise RuntimeError("Khong link duoc nvstreammux -> nvinfer")
    if not pgie.link(nvvidconv):
        raise RuntimeError("Khong link duoc nvinfer -> nvvideoconvert")
    if not nvvidconv.link(nvosd):
        raise RuntimeError("Khong link duoc nvvideoconvert -> nvdsosd")
    if not nvosd.link(sink):
        raise RuntimeError("Khong link duoc nvdsosd -> sink")

    osdsinkpad = nvosd.get_static_pad("sink")
    if not osdsinkpad:
        raise RuntimeError("Khong lay duoc sink pad cua nvosd")
    osdsinkpad.add_probe(Gst.PadProbeType.BUFFER, osd_sink_pad_buffer_probe, 0)

    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

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
