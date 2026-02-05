# A project using Amaranth HDL for testing a particle detector ASIC

## Overview

This project leverages the Amaranth HDL to test a particle detector ASIC design. It includes a bunch of counters to count pulses from the detector, and a serial protocol to start/stop/reset and read the counters. 


## Features

- Written in Python using Amaranth HDL.
- Simulates and verifies the counter's behavior.
- Designed for integration with particle detector systems.

## Requirements

- Python 3.10<=>3.14
- Amaranth HDL library.

## Getting Started

1. Clone the repository:
    ```bash
    git clone <repository_url>
    cd ASIC_Counter
    ```
2. Install dependencies using uv:
    ```bash
    uv venv create --python=3.13
    uv pip install -e .[dev]
    ```
3. Run tests:
    ```bash
    uv run pytest
    ```
4. Build and program the FPGA:
    ```bash
    uv run python -m asic_counter.top --program
    ```
5. Optionally, specify the number of counter channels:
    ```bash
    uv run python -m asic_counter.top --program --channels-count 16
    ```

## License

This project is licensed under the GPL-3.0-or-later License. See the [LICENSE](COPYING) file for details.