import cocotb

from cocotb.triggers import Timer, RisingEdge
from cocotb.clock import Clock
from asic_counter.test_runner import run_cocotb, reset_dut
from asic_counter.protocol import Encoder

class FakeUART:
    def __init__(self, dut:Encoder):
        self.dut:Encoder = dut
        self.data = []
        self.dut.uart_rdy.value = 1
        self.task = cocotb.start_soon(self.send())
    
    async def send(self):
        self.dut.uart_rdy.value = 1
        while True:
            if self.dut.uart_ack.value == 0:
                await RisingEdge(self.dut.uart_ack)
            self.dut.uart_rdy.value = 0
            self.data.append(int(self.dut.uart_data_out.value))
            await Timer(100, units="ns")  # Simulate some delay for the UART to process the data
            self.dut.uart_rdy.value = 1

async def send_data(dut:Encoder, values):
    dut.in_ack.value = 1
    for value in values:
        if dut.in_rdy.value == 0:
            await dut.in_rdy.rising_edge
        dut.data_in.value = value
        await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.eof.value = 1
    await RisingEdge(dut.clk)
    dut.in_ack.value = 0
    
    
@cocotb.test()
async def test_protocol_simple_cmds(dut:Encoder):
    # Drive inputs (Amaranth signals become Verilog ports)
    clk_gen = cocotb.start_soon(Clock(dut.clk, 1000 // 12, units="ns").start())
    dut.in_ack.value = 0
    dut.eof.value = 0
    await reset_dut(dut)
    uart = FakeUART(dut)
    await send_data(dut, values=[1, 2, 3, 4])
    await RisingEdge(dut.clk)
    

def broken_test_protocol():
    run_cocotb(Encoder)