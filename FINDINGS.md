# FINDINGS — Project 1 · Stephanie Saintil

## Score

| suite | released (8) | hidden (10) |
|-----------------------------------------|--------------|--------------------|
| Project 1 tb | /8 | /20 |


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

| Mutant | What it changes | Reachable by my stimulus? | Observable by my checks? | Why it survived |
|--------|-----------------|---------------------------|--------------------------|-----------------|
|        |                 | yes / no                  | yes / no                 |  |

## What I changed, and what it bought

| Change | Score before | Score after | Which survivors it caught |
|--------|-------------:|------------:|---------------------------|
|        |              |             |  |

## Residual risk

What this suite still cannot catch, stated plainly. Name a fault class, not a
mutant id — the pool is a sample, not the population.

1.
2.

**If I had another day:** <the one thing you would do next, and why that one>


## The distribution I ran (from the log)
  occupancy 0:685 1:410 2:353 3:372 4:346 5:371 6:363 7:435 8:665
  wr_full: 450 rd_empty: 463 both: 226
