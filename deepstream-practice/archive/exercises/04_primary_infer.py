#!/usr/bin/env python3
"""
Exercise 04: Primary inference.

Pipeline:
    filesrc -> h264parse -> nvv4l2decoder -> nvstreammux -> nvinfer
    -> nvvideoconvert -> nvdsosd -> sink

Mục tiêu:
- Hiểu `nvinfer` được cấu hình qua `config-file-path`.
- Chạy một pipeline object detection tối thiểu và đối chiếu với file gốc.

Cách chạy:
    python3 archive/exercises/04_primary_infer.py /path/to/sample.h264
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


MUXER_BATCH_TIMEOUT_USEC = 33000
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PGIE_CONFIG_PATH = os.path.join(PROJECT_ROOT, "dstest1_pgie_config.txt")


def on_message(bus, message, loop):
    if message.type == Gst.MessageType.EOS:
        print("EOS: primary infer xong.")
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

    pipeline = Gst.Pipeline.new("exercise-04-pipeline")
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

    if os.environ.get("USE_NEW_NVSTREAMMUX") != "yes":
        streammux.set_property("width", 1920)
        streammux.set_property("height", 1080)
        streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)

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

    if not streammux.link(pgie):
        raise RuntimeError("Không link được nvstreammux -> nvinfer")
    if not pgie.link(nvvidconv):
        raise RuntimeError("Không link được nvinfer -> nvvideoconvert")
    if not nvvidconv.link(nvosd):
        raise RuntimeError("Không link được nvvideoconvert -> nvdsosd")
    if not nvosd.link(sink):
        raise RuntimeError("Không link được nvdsosd -> sink")

    bus = pipeline.get_bus()
    loop = GLib.MainLoop()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

    print("Running primary infer exercise...")
    print("config-file-path =", PGIE_CONFIG_PATH)
    pipeline.set_state(Gst.State.PLAYING)

    try:
        loop.run()
    except KeyboardInterrupt:
        print("Stop by user.")
    finally:
        pipeline.set_state(Gst.State.NULL)

    # TODO: Đổi sang file config variant trong `07_config_variants/`.
    # TODO: Thay đổi `pre-cluster-threshold` và quan sát bbox thay đổi ra sao.
    # TODO: In thêm `pgie.get_property("batch-size")` và đối chiếu với muxer.
    #
    # SELF-CHECK:
    # - `nvinfer` lấy model ở đâu nếu code chỉ truyền `config-file-path`?
    # - Tại sao `nvstreammux` vẫn nằm trước `nvinfer` trong bài 1 source?
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
