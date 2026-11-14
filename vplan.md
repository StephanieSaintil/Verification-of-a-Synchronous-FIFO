# Verification plan — fifo.sv

**Author: Stephanie Saintil**   **Spec version: dut/specs/fifo.md**   **Date: 11/14/2026**

## 1. Scope

**In scope:** This plan verifies the functionality fifo using constrained-random stimulus and directed tests. 
                It covers reset behaviors, status flags, count, and the ordering of the output data.
                
**Out of scope:** Verification does not include behaviors for non-default WIDTHS or DEPTHS.

**Assumptions about the environment:** rising-edge clock, active-low synchronous reset

## 2. Feature list

| ID | Feature | Req | Priority | How it is verified |
|----|---------|-----|----------|--------------------|
| F1 | DEPTH and WIDTH Parameters: correct behavior for 8-bit data and capacity of 8 entries| fifo.md lines 6-7 "Parameters"| H | directed + CRV |
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

Coverpoints and their bins. A cross earns its place only if the interaction is
where a bug would hide — say which bug.

| ID | Coverpoint | Bins | Why these bins |
|----|-----------|------|----------------|
| C1 |           |      |  |

**Crosses**

| ID | Cross | The interaction it is aimed at |
|----|-------|-------------------------------|
| X1 |       |  |

**Illegal / ignore bins:** <what is excluded and on what authority in the spec>

## 4. Test matrix

Every feature maps to at least one test; every test traces back to a feature.
An untraceable test is a test nobody can defend.

| Test | Features | Kind | Pass criterion |
|------|----------|------|----------------|
|      |          | directed / random / assertion / formal | |

## 5. Risk and spec ambiguity

| # | Ambiguity or risk | Where in the spec | How I resolved it | Residual |
|---|-------------------|-------------------|-------------------|----------|
| 1 |                   |                   | asked / assumed / tested both | |

## 6. Closure criteria

State the numbers *before* you start, so closure is a measurement and not a
negotiation.

- Functional coverage target: **90%** of the model in section 3
- Mutation target: **18/20** on the hidden pool
- Assertions: every property paired with a passing `cover` (no vacuous passes)
- What I will report as **not verified**:
