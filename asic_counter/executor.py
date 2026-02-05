import os
import subprocess
import argparse

from amaranth import *

from .commands import Commands 

class Executor(Elaboratable):
    def __init__(self, channels_count=10):
        super().__init__()
        self.decoder_cmd = Signal(3)
        self.decoder_value = Signal(16)
        self.decoder_rdy = Signal()
        self.decoder_ack = Signal()
        
        self.counters_en = Signal(channels_count)
        self.counters_rst = Signal(channels_count)
        self.counters_value = [Signal(16) for _ in range(channels_count)]
        
    def elaborate(self, platform):
        m = Module()
        
        with m.FSM(init="IDLE") as fsm:
            with m.State("IDLE"):
                with m.If(self.out_rdy):
                    with m.Switch(self.decoder_cmd):
                        with m.Case(Commands.Enable.value):
                            m.d.sync += self.counters_en.eq(self.decoder_value[0:self.counters_en.nbits])
                        with m.Case(Commands.Reset.value):
                            m.d.sync += self.counters_rst.eq(self.decoder_value[0:self.counters_rst.nbits])
                        with m.Case(Commands.Read.value):
                            # For simplicity, we just return the value of the first counter
                            m.d.sync += self.decoder_value.eq(self.counters_value[0])
                    m.d.sync += self.decoder_ack.eq(1)
        
        return m
    
    