"""STUDENT STARTER -- Week 5 constrained-random FIFO testbench (pyvsc).

Goal: replace directed stimulus with a @vsc.randobj transaction and a proper
scoreboard so the constrained-random suite finds the whole FIFO mutant pool.

Right now this is deliberately weak: the transaction is uniform random (no bias
toward the boundaries), the run is short, and the scoreboard checks *only*
count. That leaves the full/empty flags, the FWFT head (rd_data), pointer wrap,
and the simultaneous-read+write corner completely unchecked -- raise the
found/total by finishing the TODOs.

Run:    make SIM=icarus
Score:  cd code && just mutate fifo_crv            # released pool
        cd code && just mutate fifo_crv hidden     # hidden pool (grading)
"""

import random
import os
from typing import Optional
from dataclasses import dataclass
from collections import Counter

import cocotb
import vsc
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from models.fifo_model import FifoModel

WIDTH = 8
DEPTH = 8
MASK = (1 << WIDTH) - 1

FILL, DRAIN = 0, 1

SEED = int(os.environ.get("SEED", "0xC0FFEE"), 0) # default = the seed you report
N_CYCLES = 4000

    
@vsc.randobj
class FifoTxn:
    def __init__(self, width=WIDTH):
        self.wr_en = vsc.rand_bit_t(1)
        self.rd_en = vsc.rand_bit_t(1)
        self.wr_data = vsc.rand_bit_t(width)

        self.count = vsc.uint32_t()     # Non-random count field

        self.roll_w = vsc.rand_uint8_t()
        self.roll_r = vsc.rand_uint8_t()
        self.phase = vsc.uint8_t(FILL)  


    @vsc.constraint
    def rolls_c(self):
        self.roll_w in vsc.rangelist(vsc.rng(0, 99))
        self.roll_r in vsc.rangelist(vsc.rng(0, 99))
        vsc.solve_order(self.roll_w, self.wr_en) 
        vsc.solve_order(self.roll_r, self.rd_en)

    @vsc.constraint
    def ops_c(self):
        with vsc.if_then(self.phase == FILL):
            self.wr_en == (self.roll_w < 85) 
            self.rd_en == (self.roll_r < 10) 

        with vsc.else_then():
            self.rd_en == (self.roll_r < 85) 
            self.wr_en == (self.roll_w < 10) 



class FifoDriver:
    """Turns transactions into pin wiggles."""

    class Phase: 
        def __init__ (self, depth=DEPTH, dwell=3):
            self.depth, self.dwell =depth,dwell
            self.phase,self.held=FILL,0

        def update(self,count):
            target = self.depth if self.phase == FILL else 0
            self.held = self.held + 1 if count == target else 0
            if self.held > self.dwell:
                self.phase = DRAIN if self.phase == FILL else FILL
                self.held = 0
            return self.phase
    
    def __init__(self, dut, period_ns=10):
        self.dut = dut
        self.phase = self.Phase(depth=DEPTH, dwell=3)
        cocotb.start_soon(Clock(dut.clk, period_ns, units="ns").start())


    async def reset(self):
        d = self.dut
        d.wr_en.value = 0
        d.rd_en.value = 0
        d.wr_data.value = 0
        d.rst_n.value = 0
        for _ in range(3):
            await RisingEdge(d.clk)
        d.rst_n.value = 1
        await FallingEdge(d.clk)

    def drive(self, txn):
        d = self.dut
        d.wr_en.value = int(txn.wr_en)
        d.rd_en.value = int(txn.rd_en)
        d.wr_data.value = int(txn.wr_data)


@dataclass
class Observed:
    """What one clock cycle looked like from the pins alone."""
    cycle: int
    wr_en: int
    rd_en: int
    wr_data: int
    count: int
    full: bool
    empty: bool
    rd_data: Optional[int]     # FWFT head; None while the DUT claims empty

class FifoMonitor:
    """Watches the pins and reconstructs what happened."""

    def __init__(self, dut):
        self.dut = dut
        self.cycle = 0

    def capture(self):
        d = self.dut
        self.cycle += 1
        empty = bool(d.empty.value)
        return Observed(self.cycle,
                        int(d.wr_en.value), int(d.rd_en.value),
                        int(d.wr_data.value), int(d.count.value),
                        bool(d.full.value), empty,
                        None if empty else int(d.rd_data.value))


class FifoScoreboard:
    def __init__(self):
        self.hist = Counter() # cycles spent at each occupancy
        self.wr_full = self.rd_empty = self.both = 0
        self.model = FifoModel(WIDTH, DEPTH)
        self.checked = 0

    def predict(self, txn):
        m = self.model

        self.wr_full += txn.wr_en and m.full
        self.rd_empty += txn.rd_en and m.empty
        self.both += txn.wr_en and txn.rd_en and not m.full and not m.empty

        m.step(txn.wr_en, txn.wr_data, txn.rd_en)

    def check(self, obs):
        m = self.model
        ok = (obs.count == m.count and obs.full == m.full
              and obs.empty == m.empty
              and (m.empty or obs.rd_data == m.head))
        if not ok:
            def hx(v):
                return "--" if v is None else f"0x{v:02X}"
            cocotb.log.error(
                f"first divergence: cycle {obs.cycle} -- "
                f"count {obs.count} vs model {m.count}, "
                f"full {int(obs.full)} vs {int(m.full)}, "
                f"empty {int(obs.empty)} vs {int(m.empty)}, "
                f"rd_data {hx(obs.rd_data)} vs head {hx(m.head)} | "
                f"pins that cycle: wr_en={obs.wr_en} rd_en={obs.rd_en} "
                f"wr_data=0x{obs.wr_data:02X}")
        assert obs.count == m.count, \
            f"cycle {obs.cycle}: count {obs.count} != model {m.count}"
        assert obs.full == m.full, \
            f"cycle {obs.cycle}: full {obs.full} != model {m.full}"
        assert obs.empty == m.empty, \
            f"cycle {obs.cycle}: empty {obs.empty} != model {m.empty}"
        if not m.empty:  # FWFT: head valid only when not empty
            assert obs.rd_data == m.head, \
                f"cycle {obs.cycle}: rd_data {obs.rd_data:#04x} != head {m.head:#04x}"
        self.checked += 1

@cocotb.test()
async def test_crv(dut):
    drv = FifoDriver(dut)
    await drv.reset()
    mon, sb = FifoMonitor(dut), FifoScoreboard()

    random.seed(SEED)
    txn = FifoTxn()

    for _ in range(N_CYCLES):   
        txn.count = sb.model.count 
        txn.phase=drv.phase.update(sb.model.count)
        txn.randomize() 
        drv.drive(txn)   

        sb.predict(txn)

        await RisingEdge(dut.clk) 
        await Timer(1,units="ns")

        sb.check(mon.capture())
        sb.hist[sb.model.count] += 1
        await FallingEdge(dut.clk)

    dut._log.info("occupancy " + " ".join(f"{o}:{sb.hist[o]}" for o in range(DEPTH + 1)))
    assert sb.wr_full, "stimulus never wrote into a full FIFO"
    assert set(sb.hist) == set(range(DEPTH + 1)), \
        f"stimulus never reached {set(range(DEPTH + 1)) - set(sb.hist)}"
    
    for name in ("wr_full", "rd_empty", "both"):
        count = getattr(sb, name)
        dut._log.info(f"{name}: {count}")
        assert count, f"stimulus never covered {name}"