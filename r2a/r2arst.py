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
        # RST parameters
        self.msd = 0
        self.sft = 0
        self.u = 0
        self.current_qi = 0
        self.next_qi = 0
        self.e = 0
        self.y = 0
        # Buffer parameters
        self.current_buffer = 0
        self.buffer_safety = 0
        self.buffer_reduce = 0
        self.buffer_minimum = 0

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
        self.buffer_min = 4
        self.buffer_red = 8
        self.buffer_saf = 16

        # Setting other RST parameters

        selected_qi = self.qi[0]
        for i in self.qi:
            if avg > i:
                selected_qi = i

        msg.add_quality_id(selected_qi)

        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        t = time.perf_counter() - self.request_time
        self.throughputs.append(msg.get_bit_length() / t)

        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass
