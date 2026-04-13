#!/usr/bin/env python3
"""
Exercise 08: Multi-source batching.

Pipeline:
    source0 -> h264parse -> nvv4l2decoder -> nvstreammux.sink_0
    source1 -> h264parse -> nvv4l2decoder -> nvstreammux.sink_1
    nvstreammux -> nvinfer -> nvvideoconvert -> nvdsosd -> fakesink

Mục tiêu:
- Hiểu batching thực sự khi có nhiều source.
- Đọc `frame_meta.pad_index` để biết frame đến từ source nào.

Cách chạy:
    python3 exercises/08_multisource_batching.py /path/to/a.h264 /path/to/b.h264
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
PGIE_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "07_config_variants", "pgie_trafficcamnet.txt"
)


def on_message(bus, message, loop):
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
        raise RuntimeError(f"Không tạo được element: {factory_name}")
    return element


def build_source_branch(index, input_path):
    source = make_element("filesrc", f"file-source-{index}")
    parser = make_element("h264parse", f"h264-parser-{index}")
    decoder = make_element("nvv4l2decoder", f"hw-decoder-{index}")

    source.set_property("location", input_path)

    return source, parser, decoder


def osd_sink_pad_buffer_probe(pad, info, user_data):
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
        print(f"usage: {args[0]} <path-to-h264-file-a> <path-to-h264-file-b>", file=sys.stderr)
        return 1

    input_paths = args[1:]
    for input_path in input_paths:
        if not os.path.exists(input_path):
            print(f"Input not found: {input_path}", file=sys.stderr)
            return 1

    Gst.init(None)

    pipeline = Gst.Pipeline.new("exercise-08-pipeline")
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

    pipeline.add(streammux)
    pipeline.add(pgie)
    pipeline.add(nvvidconv)
    pipeline.add(nvosd)
    pipeline.add(sink)

    for index, input_path in enumerate(input_paths):
        source, parser, decoder = build_source_branch(index, input_path)
        pipeline.add(source)
        pipeline.add(parser)
        pipeline.add(decoder)

        if not source.link(parser):
            raise RuntimeError(f"Không link được source {index} -> parser")
        if not parser.link(decoder):
            raise RuntimeError(f"Không link được parser {index} -> decoder")

        sinkpad = streammux.request_pad_simple(f"sink_{index}")
        srcpad = decoder.get_static_pad("src")
        if not sinkpad or not srcpad:
            raise RuntimeError(f"Không lấy được pad cho source {index}")
        if srcpad.link(sinkpad) != Gst.PadLinkReturn.OK:
            raise RuntimeError(f"Không link được decoder {index} vào nvstreammux")

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
    osd_sink_pad.add_probe(Gst.PadProbeType.BUFFER, osd_sink_pad_buffer_probe, None)

    bus = pipeline.get_bus()
    loop = GLib.MainLoop()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

    print("Running multi-source batching exercise...")
    pipeline.set_state(Gst.State.PLAYING)

    try:
        loop.run()
    except KeyboardInterrupt:
        print("Stop by user.")
    finally:
        pipeline.set_state(Gst.State.NULL)

    # TODO: Thử dùng cùng 1 file cho cả hai source và xem `pad_index` thay đổi thế nào.
    # TODO: Thử đổi `batch-size` sai khác với số source và đọc log / hành vi.
    # TODO: In thêm tổng object theo từng `pad_index`.
    #
    # SELF-CHECK:
    # - `pad_index` giúp bạn biết điều gì?
    # - Vì sao bài multi-source cần request `sink_0`, `sink_1`, ...?
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
