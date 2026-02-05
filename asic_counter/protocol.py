import os
import subprocess
import argparse

from amaranth import *

class Protocol(Elaboratable):
    
    def __init__(self):
        super().__init__()
        self.data_in = Signal(8)
        self.in_rdy = Signal()
        self.in_ack = Signal()
        
        self.cmd = Signal(3)
        self.value = Signal(16)
        self.out_rdy = Signal()
        self.out_ack = Signal()
        
    def elaborate(self, platform):
        m = Module()
        
        m.d.comb += self.in_ack.eq(1)
        
        # Simple protocol: first byte is command, next two bytes are value
        with m.FSM(init="Wait for start word") as fsm:
            with m.State("Wait for start word"):
                with m.If((self.in_rdy) & (self.data_in == 0xA5)):
                    m.next = "Wait second start word"
            with m.State("Wait second start word"):
                with m.If(self.in_rdy):
                    with m.If(self.data_in == 0x0F):
                        m.next = "Receive command"
                    with m.Else():
                        m.next = "Wait for start word"
            with m.State("Receive command"):
                with m.If(self.in_rdy):
                    m.d.sync += [
                        self.cmd.eq(self.data_in[0:3])
                    ]
                    m.next = "Receive value LSB"
            with m.State("Receive value LSB"):
                with m.If(self.in_rdy):
                    m.d.sync += [
                        self.value[0:8].eq(self.data_in)
                    ]
                    m.next = "Receive value MSB"

            with m.State("Receive value MSB"):
                with m.If(self.in_rdy):
                    m.d.sync += [
                        self.value[8:16].eq(self.data_in)
                    ]
                    m.next = "Output ready"
            with m.State("Output ready"):
                m.d.sync += self.out_rdy.eq(1)
                with m.If(self.out_ack):
                    m.d.sync += self.out_rdy.eq(0)
                    m.next = "Wait for start word"  
        
        return m