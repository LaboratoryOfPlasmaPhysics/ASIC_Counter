import os
import subprocess
import argparse

from amaranth import *
from amaranth.build import *
from amaranth_boards.resources import *
from amaranth_boards.icebreaker import *
from amaranth_stdio.serial import AsyncSerial 

pins_icebreaker = [
    Resource("pulses_1", 0, Pins("4  2 47 45  3 48 46 44", dir="i"),
         Attrs(IO_STANDARD="SB_LVCMOS")),
    Resource("pulses_2", 0, Pins("43 38", dir="i"),
         Attrs(IO_STANDARD="SB_LVCMOS")),
    Resource("Mux", 0, Pins("26 23 20 18", dir="o"), Attrs(IO_STANDARD="SB_LVCMOS")), 
]


class Top(Elaboratable):
   
    def __init__(self, channels_count=10):
        super().__init__()
        self.channels_count = channels_count
        
        
    def elaborate(self, platform:Platform) -> Module:
        # our Module `m` will hold all combinatoral and synchronous statements, and optionally submodules
        m = Module()
        
        pulses_1 = platform.request("pulses_1")
        pulses_2 = platform.request("pulses_2")
        user_btn = platform.request("button")
        uart_pins = platform.request("uart")
        mux = platform.request("Mux")
        led_r = platform.request("led_r")
        led_g = platform.request("led_g")
        print(f"System clock frequency: {platform.default_clk_frequency} Hz")
        
        uart = m.submodules.uart = AsyncSerial(pins=uart_pins, divisor=int(platform.default_clk_frequency // 921600))

        # loopback test
        m.d.comb += [
            led_g.o.eq(user_btn.i),
            uart.rx.ack.eq(1),
        ]
        
        with m.FSM(init="IDLE") as fsm:
            with m.State("IDLE"):
                with m.If(uart.rx.rdy):
                    m.d.comb += [ uart.tx.ack.eq(1),
                        uart.tx.data.eq(uart.rx.data)]
                    m.next = "WAIT"
            with m.State("WAIT"):
                m.d.comb += [ uart.tx.ack.eq(0) ]
                
                m.next = "IDLE"
                    
        
        return m



if __name__ == "__main__":
    args = argparse.ArgumentParser(description="Build and optionally program the FPGA")
    args.add_argument("--program", action="store_true", help="Program the FPGA after building")
    args.add_argument("--channels-count", type=int, default=10, help="Number of counter channels to build")
    args = args.parse_args()
    plat = ICEBreakerPlatform()
    plat.add_resources(pins_icebreaker)
    plat.build(Top(channels_count=args.channels_count), do_program=args.program, debug_verilog=True)