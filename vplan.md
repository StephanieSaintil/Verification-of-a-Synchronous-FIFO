# Verification plan — fifo.sv

**Author: Stephanie Saintil**   **Spec version: dut/specs/fifo.md**   **Date: 11/14/2026**

## 1. Scope

**In scope:** This plan verifies the functionality fifo using constrained-random stimulus and directed tests. 
                It covers reset behaviors, status flags, count, and the ordering of the output data.
                
**Out of scope:** Verification does not guarantee behaviors for all pointer wrap inputs .

**Assumptions about the environment:** rising-edge clock, active-low synchronous reset

## 2. Feature list

| ID | Feature | Req | Priority | How it is verified |
|----|---------|-----|----------|--------------------|
| F1 | DEPTH and WIDTH Parameters: correct behavior for multiple WIDTHS and DEPTHS | fifo.md lines 6-7 "Parameters"| H | directed + CRV |
| F2 | Full flag: asserts when count reaches DEPTH | fifo.md line 28 Behavior #5| H | CRV |
| F3 | Empty flag: asserts when count reaches 0 | fifo.md line 28 Behavior #5| H | CRV |
| F4 | Reset behavior: count and full reaches 0 and empty flag is asserted | fifo.md line 21 Behavior #1| H | directed |
| F5 | fifo ordering: earliest written data is always read first | fifo.md line 29 Behavior #6| H | CRV |
| F6 | Read only: if not empty reads are accepted when read is enabled | fifo.md line 24 Behavior #2 | H | CRV |
| F7 | Write only: if not full writes are accepted when write is enabled  | fifo.md line 22 Behavior #5| H | CRV |
| F8 | Simultaneous read and write: this does not change count | fifo.md line 26-27 Behavior #4| H | CRV |
| F9 | Read while empty: ignored by the fifo | fifo.md line 25 Behavior #3| H | CRV |
| F10 | Write while full: dropped and causes no corruption to the current data | fifo.md line 23 Behavior #2| H | CRV |

## 3. Coverage model

| ID | Coverpoint | Bins | Why these bins |
|----|-----------|------|----------------|
| C1 |  Reset | asserted when empty and !empty, asserted with rd_en and wr_en | Tests whether outputs are correct after reset|
| C2 |  Boundaries | empty, full, near full, near empty | Confirms correctness of operations during transitions to full and empty  |
| C3 |  Pointer wrap | advance read and write pointers to full and empty| Detects any skipped positions for reading and writing transactions |
| C4 |  Output ordering | Read until empty, random intervals of read and writes| Verifies that first entered data is read first |
| C5 |  Status flags | full = 1, full =0, empty = 1, empty = 0 | Checks that the status flag are being asserted correctly |
| C6 |  Read | rd_en = 1, rd_en = 0, read while full, read while empty   | Checks read behavior and that reads are ignored at empty |
| C7 |  Write | wr_en = 1, wr_en = 0, write while empty, write while full     |  Checks write behavior and that writes are dropped when full    |
| C8 |  Simultaneous read and writes | both rd_en and wr_en = 0, both rd_en and wr_en = 1 | Confirms that count remains unchanged |
| C9 |  Parameterization | defaults, (WIDTH = 7, DEPTH = 5), (WIDTH = 16, DEPTH = 16), (WIDTH = 32, DEPTH = 32) | Ensures correctness is not corrupted for smaller and larger parameters. |

**Crosses**

| ID | Cross | The interaction it is aimed at |
|----|-------|-------------------------------|
| X1 |   status flags x count    | Detects incorrect full or empty flags at the current count |
| X2 |   simultaneous operations x  boundaries   | Catches bugs that specifically occur when both read and writes are attempted at full or empty|
| X3 |   simultaneous operations x pointer wrap around   | Detects pointer inconsistency bugs when both read and writes occur  |
| X4 |  reset x rd_data  | Detects any output corruption occurring after reset |


**Illegal / ignore bins:** < 1. By the definition of full and empty in the spec full and empty cannot be asserted at the same time.
                              2. Count is defined in the range of 0 - DEPTH only. Count cannot go beyond the depth specified.>

## 4. Test matrix

Every feature maps to at least one test; every test traces back to a feature.
An untraceable test is a test nobody can defend.

| Test | Features | Kind | Pass criterion |
|------|----------|------|----------------|
| basic read/write   | F6 & F7  | CRV | Accepted read results in count - 1, Accepted write results in count + 1 |
| write when full |  | CRV | Accepted read results in count - 1, Accepted write results in count + 1 |

## 5. Risk and spec ambiguity

| # | Ambiguity or risk | Where in the spec | How I resolved it | Residual |
|---|-------------------|-------------------|-------------------|----------|
| 1 | output of wr_en and rd_en when rst_n = 0 |  fifo.md line 21 Behavior #1 | assumed both default to 0 and will test during reset | No direct confirmation detailed in the spec although covered by testing |
| 2 | What happens to data currently stored in the fifo if rst_n = 0 while !empty?  |  fifo.md line 21 Behavior #1 | Tested by doing read operations immediately after resetting non-empty fifo. | Is the data still reachable or completely lost? |

## 6. Closure criteria

State the numbers *before* you start, so closure is a measurement and not a
negotiation.

- Functional coverage target: **90%** of the model in section 3
- Mutation target: **18/20** on the hidden pool
- Assertions: 1. Count: C1, C2, C8, and C3
              2. Full and Empty: C5
              3. rd_data: C4
- What I will report as **not verified**: Verification does not include

