#!/usr/bin/env python3
"""
Exercise 01: GStreamer bootstrap.

Mục tiêu:
- Hiểu bộ khung tối thiểu của một app GStreamer.
- Hiểu `Gst.init`, `Pipeline`, bus, main loop, state transition.

Cách chạy:
    python3 archive/exercises/01_gst_bootstrap.py /path/to/any-file

WHY IT MATTERS:
- DeepStream được xây trên GStreamer. Nếu bạn chưa nhìn rõ bộ khung này,
  các plugin DeepStream ở bài sau sẽ rất khó "vào đầu".
"""

import os
import sys

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst


def on_message(bus, message, loop):
    message_type = message.type

    if message_type == Gst.MessageType.EOS:
        print("EOS: pipeline đã đọc hết dữ liệu.")
        loop.quit()
    elif message_type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(f"ERROR: {err}")
        if debug:
            print(f"DEBUG: {debug}")
        loop.quit()
    elif message_type == Gst.MessageType.STATE_CHANGED:
        src = message.src
        if src and src.get_name() == "exercise-01-pipeline":
            old_state, new_state, pending = message.parse_state_changed()
            print(
                "PIPELINE STATE:",
                old_state.value_nick,
                "->",
                new_state.value_nick,
                f"(pending={pending.value_nick})",
            )

    return True


def main(args):
    if len(args) != 2:
        print(f"usage: {args[0]} <path-to-any-file>", file=sys.stderr)
        return 1

    input_path = args[1]
    if not os.path.exists(input_path):
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 1

    Gst.init(None)

    pipeline = Gst.Pipeline.new("exercise-01-pipeline")
    source = Gst.ElementFactory.make("filesrc", "file-source")
    sink = Gst.ElementFactory.make("fakesink", "fake-sink")

    if not pipeline or not source or not sink:
        print("Không tạo được pipeline hoặc element.", file=sys.stderr)
        return 1

    source.set_property("location", input_path)

    pipeline.add(source)
    pipeline.add(sink)

    if not source.link(sink):
        print("Không link được filesrc -> fakesink", file=sys.stderr)
        return 1

    bus = pipeline.get_bus()
    loop = GLib.MainLoop()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

    print("Bắt đầu PLAYING")
    pipeline.set_state(Gst.State.PLAYING)

    try:
        loop.run()
    except KeyboardInterrupt:
        print("Dừng bởi người dùng.")
    finally:
        print("Trả pipeline về NULL")
        pipeline.set_state(Gst.State.NULL)

    # TODO: In ra tên từng element trong pipeline bằng pipeline.iterate_elements().
    # TODO: Thử bỏ bus watch và xem app còn biết EOS/ERROR không.
    # TODO: Thử đổi `fakesink` thành `filesink` để thấy lượng byte đi qua pipeline.
    #
    # SELF-CHECK:
    # - Tại sao app cần `GLib.MainLoop()`?
    # - `set_state(Gst.State.NULL)` giải phóng điều gì ở mức khái niệm?
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
