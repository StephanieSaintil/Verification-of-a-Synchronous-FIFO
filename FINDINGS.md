# FINDINGS — <Homework 5> · <Stephanie Saintil>

## Score

| suite | released (8) | hidden (10) |
|-----------------------------------------|--------------|--------------------|
| HW4 directed | 8/8 | 12/15 |
| HW5 CRV, seed 0xC0FFEE, 4000 cycles | 8/8 | 15/20 |

**Command run:**

```bash
source /opt/course/cocotb-env/bin/activate
just test fifo_crv icarus
just mutate fifo_crv
```
## Survivors

One row per mutant your suite did not find. `Reachable?` is the important
column: a survivor you never reached is a *stimulus* problem, a survivor you
reached but did not notice is a *checking* problem, and they have different
fixes.

## What CRV found that the directed suite missed
- Both the directed and CRV suites caught the 8 released mutants. On the hidden pool,
the CRV caught the last hard mutant raising from 7/8 and caught 2 additonal hard muatants.

## Residual risk

What this suite still cannot catch, stated plainly. Name a fault class, not a
mutant id — the pool is a sample, not the population.

None of the very hard hard mutants were caught for both Homework 4 & 5
which are all most likely due to no constraint puts stimulus in these corners.

1. This suite can possibly miss bugs related to reset being asserted when count >= 1. (reachability)
2. It could also miss any incorrect counts that might arise from writing the same data for multiple cycles. (reachability)

**If I had another day:** < Add additional costraints, add directed tests or phases that specifically target any reset mutants >


## The distribution I ran (from the log)
  occupancy 0:685 1:410 2:353 3:372 4:346 5:371 6:363 7:435 8:665
  wr_full: 450 rd_empty: 463 both: 226