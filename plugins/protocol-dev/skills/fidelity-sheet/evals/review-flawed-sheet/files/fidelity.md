# BeeAdHoc: fidelity sheet

## Sources

| Key | Citation | Access |
|---|---|---|
| PG460 | Farooq, Wedde et al., BeeAdHoc PG 460 final report, University of Dortmund, 2006, hdl 2003/22405 | in hand |

## Mechanisms

| Mechanism | Source | Implementation | Status |
|---|---|---|---|
| Scouts discover routes by flooding | [PG460] §4.2 | `core/scout` | as written |
| Foragers carry data along the dance floor's best route | the paper | `core/forager` | as written |
| Expanding ring search for scouts | | `core/scout` | |

## Parameters

| Parameter | Value | Source | Notes |
|---|---|---|---|
| Scout TTL start | 2 | [PG460] Table 7.1 | |
| Forager lifetime | 30 s | | from the AntHocNet arm |
| Dance-floor size | 64 | repo choice | |
| Battery threshold | 20 % | [GECCO05] §3 | |

## Anchor candidate

| Trend | Scenario | Metric | Comparators | Source |
|---|---|---|---|---|
| BeeAdHoc has the lowest control overhead | PG 460 ch. 7 setup | NRL | AODV, DSR, DSDV | PG 460 chapter 7 |
