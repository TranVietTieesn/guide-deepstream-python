#!/usr/bin/env python3
"""
Exercise 06: OSD overlay and object counts.

Pipeline:
    filesrc -> h264parse -> nvv4l2decoder -> nvstreammux -> nvinfer
    -> nvvideoconvert -> nvdsosd -> sink

Mục tiêu:
- Dùng metadata để tạo text overlay.
- Đổi màu bbox theo class để thấy metadata được "visualize" như thế nào.

Cách chạy:
    python3 archive/exercises/06_osd_overlay_counts.py /path/to/sample.h264
"""

import os
import sys

sys.path.append(
    "/home/vtea/opt/nvidia/deepstream/deepstream-9.0/sources/deepstream_python_apps/apps"
)

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst

from common.platform_info import PlatformInfo
import pyds


PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3
MUXER_BATCH_TIMEOUT_USEC = 33000
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PGIE_CONFIG_PATH = os.path.join(PROJECT_ROOT, "dstest1_pgie_config.txt")


def on_message(bus, message, loop):
    if message.type == Gst.MessageType.EOS:
        print("EOS: overlay exercise xong.")
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
        raise RuntimeError(f"Không tạo được element: {factory_name}")
    return element


def create_sink(platform_info):
    if platform_info.is_integrated_gpu():
        return make_element("nv3dsink", "video-output")
    if platform_info.is_platform_aarch64():
        return make_element("nv3dsink", "video-output")
    return make_element("nveglglessink", "video-output")


def colorize_object(obj_meta):
    if obj_meta.class_id == PGIE_CLASS_ID_PERSON:
        obj_meta.rect_params.border_color.set(0.0, 1.0, 0.0, 0.9)
    elif obj_meta.class_id == PGIE_CLASS_ID_VEHICLE:
        obj_meta.rect_params.border_color.set(1.0, 0.0, 0.0, 0.9)
    elif obj_meta.class_id == PGIE_CLASS_ID_BICYCLE:
        obj_meta.rect_params.border_color.set(0.0, 0.7, 1.0, 0.9)
    else:
        obj_meta.rect_params.border_color.set(1.0, 1.0, 0.0, 0.9)


def osd_sink_pad_buffer_probe(pad, info, user_data):
    gst_buffer = info.get_buffer()
    if not gst_buffer:
        print("Unable to get GstBuffer")
        return Gst.PadProbeReturn.OK

    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    l_frame = batch_meta.frame_meta_list

    while l_frame is not None:
        try:
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            break

        obj_counter = {
            PGIE_CLASS_ID_VEHICLE: 0,
            PGIE_CLASS_ID_PERSON: 0,
            PGIE_CLASS_ID_BICYCLE: 0,
            PGIE_CLASS_ID_ROADSIGN: 0,
        }

        l_obj = frame_meta.obj_meta_list
        while l_obj is not None:
            try:
                obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
            except StopIteration:
                break

            obj_counter[obj_meta.class_id] = obj_counter.get(obj_meta.class_id, 0) + 1
            colorize_object(obj_meta)

            try:
                l_obj = l_obj.next
            except StopIteration:
                break

        display_meta = pyds.nvds_acquire_display_meta_from_pool(batch_meta)
        display_meta.num_labels = 1
        text_params = display_meta.text_params[0]
        text_params.display_text = (
            "Frame={} Objects={} Vehicle={} Person={} Bicycle={} RoadSign={}".format(
                frame_meta.frame_num,
                frame_meta.num_obj_meta,
                obj_counter[PGIE_CLASS_ID_VEHICLE],
                obj_counter[PGIE_CLASS_ID_PERSON],
                obj_counter[PGIE_CLASS_ID_BICYCLE],
                obj_counter[PGIE_CLASS_ID_ROADSIGN],
            )
        )
        text_params.x_offset = 10
        text_params.y_offset = 12
        text_params.font_params.font_name = "Serif"
        text_params.font_params.font_size = 14
        text_params.font_params.font_color.set(1.0, 1.0, 1.0, 1.0)
        text_params.set_bg_clr = 1
        text_params.text_bg_clr.set(0.0, 0.0, 0.0, 1.0)

        print(pyds.get_string(text_params.display_text))
        pyds.nvds_add_display_meta_to_frame(frame_meta, display_meta)

        try:
            l_frame = l_frame.next
        except StopIteration:
            break

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
    platform_info = PlatformInfo()

    pipeline = Gst.Pipeline.new("exercise-06-pipeline")
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
    streammux.set_property("width", 1920)
    streammux.set_property("height", 1080)
    streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)
    pgie.set_property("config-file-path", PGIE_CONFIG_PATH)

    for element in (source, parser, decoder, streammux, pgie, nvvidconv, nvosd, sink):
        pipeline.add(element)

    if not source.link(parser):
        raise RuntimeError("Không link được filesrc -> h264parse")
    if not parser.link(decoder):
        raise RuntimeError("Không link được h264parse -> nvv4l2decoder")

    sinkpad = streammux.request_pad_simple("sink_0")
    srcpad = decoder.get_static_pad("src")
    if not sinkpad or not srcpad:
        raise RuntimeError("Không lấy được pad để nối vào nvstreammux")
    if srcpad.link(sinkpad) != Gst.PadLinkReturn.OK:
        raise RuntimeError("Không link được decoder.src -> streammux.sink_0")

    for upstream, downstream, label in (
        (streammux, pgie, "nvstreammux -> nvinfer"),
        (pgie, nvvidconv, "nvinfer -> nvvideoconvert"),
        (nvvidconv, nvosd, "nvvideoconvert -> nvdsosd"),
        (nvosd, sink, "nvdsosd -> sink"),
    ):
        if not upstream.link(downstream):
            raise RuntimeError(f"Không link được {label}")

    osd_sink_pad = nvosd.get_static_pad("sink")
    if not osd_sink_pad:
        raise RuntimeError("Không lấy được nvosd sink pad")
    osd_sink_pad.add_probe(
        Gst.PadProbeType.BUFFER,
        osd_sink_pad_buffer_probe,
        None,
    )

    bus = pipeline.get_bus()
    loop = GLib.MainLoop()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

    print("Running overlay exercise...")
    pipeline.set_state(Gst.State.PLAYING)

    try:
        loop.run()
    except KeyboardInterrupt:
        print("Stop by user.")
    finally:
        pipeline.set_state(Gst.State.NULL)

    # TODO: Thêm dòng text mới hiện tổng số object theo frame.
    # TODO: Đổi màu bbox theo quy tắc riêng của bạn.
    # TODO: Thêm logic chỉ hiện overlay cho `person`.
    #
    # SELF-CHECK:
    # - Bbox color được đổi ở đâu?
    # - Text overlay được tạo từ `NvDsDisplayMeta` như thế nào?
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
