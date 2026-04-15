#!/usr/bin/env python3
"""
Lesson 02 reference: read and release custom user meta.
"""

import sys

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst

import pyds


def bus_call(bus, message, loop):
    t = message.type
    if t == Gst.MessageType.EOS:
        print("End-of-stream")
        loop.quit()
    elif t == Gst.MessageType.WARNING:
        err, debug = message.parse_warning()
        print("Warning: %s: %s" % (err, debug))
    elif t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        sys.stderr.write("Error: %s: %s\n" % (err, debug))
        loop.quit()
    return True


def fakesink_sink_pad_buffer_probe(pad, info, u_data):
    gst_buffer = info.get_buffer()
    if not gst_buffer:
        print("Unable to get GstBuffer")
        return Gst.PadProbeReturn.OK

    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    if not batch_meta:
        return Gst.PadProbeReturn.OK

    pyds.nvds_acquire_meta_lock(batch_meta)

    l_frame = batch_meta.frame_meta_list
    while l_frame is not None:
        try:
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            break

        l_usr = frame_meta.frame_user_meta_list
        while l_usr is not None:
            try:
                user_meta = pyds.NvDsUserMeta.cast(l_usr.data)
            except StopIteration:
                break

            if user_meta.base_meta.meta_type == pyds.NvDsMetaType.NVDS_USER_META:
                custom_msg_meta = pyds.CustomDataStruct.cast(user_meta.user_meta_data)
                print(
                    "event msg meta, otherAttrs = %s"
                    % pyds.get_string(custom_msg_meta.message)
                )
                print("custom meta structId:: ", custom_msg_meta.structId)
                print("custom meta msg:: ", pyds.get_string(custom_msg_meta.message))
                print("custom meta sampleInt:: ", custom_msg_meta.sampleInt)
                pyds.release_custom_struct(custom_msg_meta)

            try:
                l_usr = l_usr.next
            except StopIteration:
                break

        try:
            l_frame = l_frame.next
        except StopIteration:
            break

    pyds.nvds_release_meta_lock(batch_meta)
    return Gst.PadProbeReturn.OK


def main(args):
    if len(args) != 2:
        sys.stderr.write("usage: %s <h264 stream file>\n" % args[0])
        sys.exit(1)

    Gst.init(None)

    pipeline = Gst.Pipeline.new("custom-user-meta-pipeline")
    source = Gst.ElementFactory.make("filesrc", "file-source")
    h264parser = Gst.ElementFactory.make("h264parse", "h264-parser")
    decoder = Gst.ElementFactory.make("nvv4l2decoder", "nvv4l2-decoder")
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    queue = Gst.ElementFactory.make("queue", "queue")
    queue1 = Gst.ElementFactory.make("queue", "queue1")
    sink = Gst.ElementFactory.make("fakesink", "fakesink")

    source.set_property("location", args[1])
    streammux.set_property("width", 1280)
    streammux.set_property("height", 720)
    streammux.set_property("batch-size", 1)

    for element in (source, h264parser, decoder, streammux, queue, queue1, sink):
        pipeline.add(element)

    source.link(h264parser)
    h264parser.link(decoder)

    sinkpad = streammux.request_pad_simple("sink_0")
    srcpad = decoder.get_static_pad("src")
    srcpad.link(sinkpad)

    streammux.link(queue)
    queue.link(queue1)
    queue1.link(sink)

    sinkpad_probe = sink.get_static_pad("sink")
    sinkpad_probe.add_probe(
        Gst.PadProbeType.BUFFER, fakesink_sink_pad_buffer_probe, 0
    )

    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)

    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except KeyboardInterrupt:
        pass
    finally:
        pipeline.set_state(Gst.State.NULL)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
