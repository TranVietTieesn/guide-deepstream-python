#!/usr/bin/env python3
"""
Exercise 05: Probe batch metadata.

Pipeline:
    filesrc -> h264parse -> nvv4l2decoder -> nvstreammux -> nvinfer
    -> nvvideoconvert -> nvdsosd -> fakesink

Mục tiêu:
- Hiểu `Gst.Buffer -> NvDsBatchMeta -> NvDsFrameMeta -> NvDsObjectMeta`.
- Hiểu vì sao sample dùng `hash(gst_buffer)` và `.cast()`.

Cách chạy:
    python3 exercises/05_probe_batch_meta.py /path/to/sample.h264
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
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PGIE_CONFIG_PATH = os.path.join(PROJECT_ROOT, "dstest1_pgie_config.txt")


def on_message(bus, message, loop):
    if message.type == Gst.MessageType.EOS:
        print("EOS: metadata probe xong.")
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

        print(
            f"Frame={frame_meta.frame_num} "
            f"pad_index={frame_meta.pad_index} "
            f"objects={frame_meta.num_obj_meta}"
        )

        l_obj = frame_meta.obj_meta_list
        while l_obj is not None:
            try:
                obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
            except StopIteration:
                break

            rect = obj_meta.rect_params
            print(
                "  "
                f"class_id={obj_meta.class_id} "
                f"confidence={obj_meta.confidence:.3f} "
                f"bbox=({rect.left:.1f},{rect.top:.1f},"
                f"{rect.width:.1f},{rect.height:.1f})"
            )

            try:
                l_obj = l_obj.next
            except StopIteration:
                break

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

    pipeline = Gst.Pipeline.new("exercise-05-pipeline")
    source = make_element("filesrc", "file-source")
    parser = make_element("h264parse", "h264-parser")
    decoder = make_element("nvv4l2decoder", "hw-decoder")
    streammux = make_element("nvstreammux", "stream-muxer")
    pgie = make_element("nvinfer", "primary-inference")
    nvvidconv = make_element("nvvideoconvert", "video-convert")
    nvosd = make_element("nvdsosd", "onscreendisplay")
    sink = make_element("fakesink", "fake-sink")

    source.set_property("location", input_path)
    streammux.set_property("batch-size", 1)
    streammux.set_property("width", 1920)
    streammux.set_property("height", 1080)
    streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)
    pgie.set_property("config-file-path", PGIE_CONFIG_PATH)
    sink.set_property("sync", False)

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
        (nvosd, sink, "nvdsosd -> fakesink"),
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

    print("Running metadata probe exercise...")
    pipeline.set_state(Gst.State.PLAYING)

    try:
        loop.run()
    except KeyboardInterrupt:
        print("Stop by user.")
    finally:
        pipeline.set_state(Gst.State.NULL)

    # TODO: Đếm object theo `class_id`.
    # TODO: Map `class_id` sang tên label bằng labels file.
    # TODO: Thử chuyển probe sang điểm khác trong pipeline và quan sát metadata.
    #
    # SELF-CHECK:
    # - Metadata object detection xuất hiện sau plugin nào?
    # - Vì sao cần `hash(gst_buffer)` khi gọi `gst_buffer_get_nvds_batch_meta`?
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
