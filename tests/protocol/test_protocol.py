import cocotb

from cocotb.triggers import Timer, RisingEdge
from cocotb.clock import Clock
from asic_counter.test_runner import run_cocotb
from asic_counter.protocol import Protocol

async def reset_dut(dut):
    dut.rst.value = 1
    for _ in range(5):  
        await RisingEdge(dut.clk)
    dut.rst.value = 0
    for _ in range(5):  
        await RisingEdge(dut.clk)

async def send_cmd(dut, cmd, value):
    # Send start sequence
    await RisingEdge(dut.clk)
    dut.data_in.value = 0xA5
    dut.in_rdy.value = 1
    await RisingEdge(dut.clk)
    
    dut.data_in.value = 0x0F
    await RisingEdge(dut.clk)
    
    # Send command 
    dut.data_in.value = cmd
    await RisingEdge(dut.clk)
    
    dut.data_in.value = value & 0xFF
    await RisingEdge(dut.clk)
    # Send value MSB
    dut.data_in.value = (value >> 8) & 0xFF
    await RisingEdge(dut.clk)
    
    
@cocotb.test()
async def test_protocol_simple_cmds(dut):
    # Drive inputs (Amaranth signals become Verilog ports)
    clk_gen = cocotb.start_soon(Clock(dut.clk, 1000 // 12, units="ns").start())
    await reset_dut(dut)
    await send_cmd(dut, cmd=0b101, value=0x1234)
    if dut.out_rdy.value == 0:
        await RisingEdge(dut.out_rdy)
    assert dut.cmd.value == 0b101, f"Expected cmd 0b101, got {dut.cmd.value}"
    assert dut.value.value == 0x1234, f"Expected value 0x1234, got {dut.value.value}"
    dut.out_ack.value = 1
    await RisingEdge(dut.clk)
    
    
@cocotb.test()
async def test_protocol_two_cmds_without_ack(dut):
    # Drive inputs (Amaranth signals become Verilog ports)
    clk_gen = cocotb.start_soon(Clock(dut.clk, 1000 // 12, units="ns").start())
    await reset_dut(dut)
    dut.out_ack.value = 0
    await send_cmd(dut, cmd=0b101, value=0x1234)
    await send_cmd(dut, cmd=0b011, value=0xABCD)
    if dut.out_rdy.value == 0:
        await RisingEdge(dut.out_rdy)
    assert dut.cmd.value == 0b101, f"Expected cmd 0b101, got {dut.cmd.value}"
    assert dut.value.value == 0x1234, f"Expected value 0x1234, got {dut.value.value}"
    dut.out_ack.value = 1
    await RisingEdge(dut.clk)
    
    

@cocotb.test()
async def test_protocol_garbage(dut):
    # Drive inputs (Amaranth signals become Verilog ports)
    clk_gen = cocotb.start_soon(Clock(dut.clk, 1000 // 12, units="ns").start())
    await reset_dut(dut)
    # Send random bytes that don't follow the protocol
    dut.data_in.value = 0xA5
    dut.in_rdy.value = 1
    dut.out_ack.value = 0
    await RisingEdge(dut.clk)
    for _ in range(10):
        dut.data_in.value = 0xFF  # Invalid byte
        await RisingEdge(dut.clk)
    await send_cmd(dut, cmd=0b010, value=0x5678)
    if dut.out_rdy.value == 0:
        await RisingEdge(dut.out_rdy)
    assert dut.cmd.value == 0b010, f"Expected cmd 0b010, got {dut.cmd.value}"
    assert dut.value.value == 0x5678, f"Expected value 0x5678, got {dut.value.value}"
    await Timer(500, units="ns")
    

def test_protocol():
    run_cocotb(Protocol)