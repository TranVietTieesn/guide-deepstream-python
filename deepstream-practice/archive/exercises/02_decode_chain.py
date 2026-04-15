#!/usr/bin/env python3
"""
Exercise 02: Decode chain.

Pipeline:
    filesrc -> h264parse -> nvv4l2decoder -> fakesink

Mục tiêu:
- Hiểu video encoded vào parser/decode ra sao.
- Hiểu vì sao sample gốc tách parser và decoder.

Cách chạy:
    python3 archive/exercises/02_decode_chain.py /path/to/sample.h264
"""

import os
import sys

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst


def on_message(bus, message, loop):
    if message.type == Gst.MessageType.EOS:
        print("EOS: decode xong.")
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


def main(args):
    if len(args) != 2:
        print(f"usage: {args[0]} <path-to-h264-file>", file=sys.stderr)
        return 1

    input_path = args[1]
    if not os.path.exists(input_path):
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 1

    Gst.init(None)

    pipeline = Gst.Pipeline.new("exercise-02-pipeline")
    source = make_element("filesrc", "file-source")
    parser = make_element("h264parse", "h264-parser")
    decoder = make_element("nvv4l2decoder", "hw-decoder")
    sink = make_element("fakesink", "fake-sink")

    source.set_property("location", input_path)
    sink.set_property("sync", False)

    for element in (source, parser, decoder, sink):
        pipeline.add(element)

    if not source.link(parser):
        raise RuntimeError("Không link được filesrc -> h264parse")
    if not parser.link(decoder):
        raise RuntimeError("Không link được h264parse -> nvv4l2decoder")
    if not decoder.link(sink):
        raise RuntimeError("Không link được nvv4l2decoder -> fakesink")

    bus = pipeline.get_bus()
    loop = GLib.MainLoop()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

    print("Running decode chain...")
    pipeline.set_state(Gst.State.PLAYING)

    try:
        loop.run()
    except KeyboardInterrupt:
        print("Stop by user.")
    finally:
        pipeline.set_state(Gst.State.NULL)

    # TODO: Thử bỏ `h264parse` để thấy vì sao decoder có thể gặp vấn đề.
    # TODO: Gắn pad probe vào `decoder.src` và ghi chú xem dữ liệu sau decode
    # đang là frame, không còn là H264 elementary stream nữa.
    # TODO: Thử đổi `fakesink` thành sink hiển thị nếu bạn muốn nhìn kết quả.
    #
    # SELF-CHECK:
    # - `filesrc` có hiểu "video" không hay chỉ đọc byte?
    # - `h264parse` và `nvv4l2decoder` khác nhau ở vai trò nào?
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
