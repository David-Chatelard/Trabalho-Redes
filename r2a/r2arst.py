"""
@author:
    David Fanchic Chatelard - 180138863
    Julia Passos Pontes - 190057904
    Laura Maciel Neves Franco - 190016078

@description:
    Implementacao utilizando o RST(Relative Smoothed Throughput)
"""

from r2a.ir2a import IR2A
from player.parser import *
import time
from statistics import mean


class R2ARST(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.throughputs = []
        self.qi = []
        self.request_time = 0
        self.has_waited = False
        # RST parameters
        self.msd = 0
        self.sft = 0
        self.u = 0
        self.current_qi = 0
        self.next_qi = 0
        self.e = 0
        self.y = 0.8
        self.index = 0
        # Buffer parameters
        self.current_buffer = 0
        self.buffer_safety = 7
        self.buffer_reduce = 5
        self.buffer_minimum = 5

    def handle_xml_request(self, msg):
        # Get the time that the segment was requested
        self.request_time = time.perf_counter()

        self.send_down(msg)

    def handle_xml_response(self, msg):
        # Get list of qualities
        parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = parsed_mpd.get_qi()

        # Set RST parameter segment fetch time
        self.sft = time.perf_counter() - self.request_time

        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        self.request_time = time.perf_counter()

        # Setting RST buffer parameters
        self.buffer_minimum = 4
        self.buffer_reduce = 8
        self.buffer_safety = 16

        # Waits for buffer to reach safety level
        if self.current_buffer < self.buffer_safety and not self.has_waited:
            msg.add_quality_id(self.qi[self.current_qi])
        else:
            self.has_waited = True
            # If it's the first segment
            if len(self.whiteboard.get_playback_qi()) == 0:
                self.current_qi = 0
            # Get last segment qi
            else:
                self.current_qi = self.whiteboard.get_playback_qi()[-1][1]

            # Setting other RST parameters
            self.msd = msg.get_segment_size()
            self.u = self.msd/self.sft
            self.next_qi = self.current_qi + \
                1 if self.current_qi != (len(self.qi) - 1) else self.current_qi
            self.e = (self.qi[self.next_qi] -
                      self.qi[self.current_qi]) / (self.qi[self.current_qi])

            self.index = self.current_qi

            # Using RST algorithm
            if self.current_buffer < self.buffer_minimum:
                if self.u >= 1:
                    self.index -= 1
                else:
                    for i in range(len(self.qi)):
                        if self.qi[i] < self.qi[self.current_qi] * self.u:
                            self.index = i

            if self.u < self.y and self.current_buffer < self.buffer_reduce:
                self.index -= 1

            if self.u > (1 + self.e) and self.current_buffer > self.buffer_safety:
                self.index += 1

            # Validating index value
            self.index = self.index if self.index < len(
                self.qi) else len(self.qi) - 1
            self.index = self.index if self.index > 0 else 0

            msg.add_quality_id(self.qi[self.index])

        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        # Get the last buffer value
        if self.whiteboard.get_playback_buffer_size():
            self.current_buffer = self.whiteboard.get_playback_buffer_size(
            )[-1][1]

        # Get the segment fetch time
        self.sft = time.perf_counter() - self.request_time

        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass
