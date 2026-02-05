from cocotb_test.simulator import run as _run
from amaranth.back import verilog
from amaranth import Signal
from tempfile import NamedTemporaryFile
import inspect
import os

def find_dut_ports(dut):
    # Heuristic: look for Signals that are not internal (e.g., not starting with "_")
    ports = []
    for name in dir(dut):
        if not name.startswith("_"):
            print(f"Checking attribute: {name}")
            attr = getattr(dut, name)
            if isinstance(attr, Signal):
                ports.append(attr)
    return ports

def caller_module_dir():
    # Look up the caller frame (one level up)
    caller_frame = inspect.stack()[2]
    caller_mod = inspect.getmodule(caller_frame[0])
    if caller_mod and caller_mod.__name__ != "__main__":
        return os.path.dirname(caller_mod.__file__)
    else:
        # Fallback to current working directory
        return os.getcwd()

def run_cocotb(dut_class, module_name=None):
    # If module_name not provided, try to infer it from the caller
    if module_name is None:
        # Look up the caller frame (one level up)
        caller_frame = inspect.stack()[1]
        caller_mod = inspect.getmodule(caller_frame[0])
        if caller_mod and caller_mod.__name__ != "__main__":
            module_name = caller_mod.__name__
        else:
            # Fallback to filename base (not guaranteed importable)
            filename = getattr(caller_frame, "filename", None) or caller_frame[1]
            module_name = os.path.splitext(os.path.basename(filename))[0]

    # 1. Generate Verilog dynamically
    dut = dut_class()
    with NamedTemporaryFile(mode="w", suffix=".v", delete=False) as f:
        # Ensure simulator has an appropriate timescale so cocotb Timer(ns) works
        f.write("`timescale 1ns/1ps\n")
        f.write(verilog.convert(dut, ports=find_dut_ports(dut)))
        f.flush()  # Ensure all data is written to disk before simulator reads it

        # 2. Run Cocotb on the generated Verilog
        _run(
            verilog_sources=[f.name],
            toplevel="top",            # Amaranth default top name is usually 'top'
            module=module_name,         # Name of your cocotb test file
            simulator="icarus",         # Or 'verilator', etc.
            waves=True,                # Enable waveform dumping for debugging
            sim_build=os.path.join(caller_module_dir(), "sim_build")
        )
