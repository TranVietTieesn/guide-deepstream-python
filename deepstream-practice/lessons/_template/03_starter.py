#!/usr/bin/env python3
"""
Starter file for a DeepStream/GStreamer lesson.

Hay doc theo thu tu:
1. `01_guide.md`
2. `02_coding_guide.md`
3. file nay
"""

import os
import sys

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst


def on_message(bus, message, loop):
    # TODO 1: Xu ly it nhat `EOS` va `ERROR`.
    # Xem `02_coding_guide.md` de biet callback nay nhan gi va dung gi.
    # TODO 2: Neu lesson can, them `STATE_CHANGED` hoac message type khac.
    return True


def main(args):
    # TODO 3: Parse argument va kiem tra input.
    input_path = None
    if not input_path or not os.path.exists(input_path):
        print("TODO: Truyen input hop le.", file=sys.stderr)
        return 1

    Gst.init(None)

    # TODO 4: Tao pipeline va element theo `01_guide.md` va `02_coding_guide.md`.
    pipeline = None
    if not pipeline:
        print("TODO: Tao pipeline truoc.", file=sys.stderr)
        return 1

    # TODO 5: Set property can thiet.
    # TODO 6: `pipeline.add(...)`.
    # TODO 7: Link static pads hoac request pads.

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
