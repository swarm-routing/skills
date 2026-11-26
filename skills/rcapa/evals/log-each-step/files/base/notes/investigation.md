# NS3-512 investigation (previous session, in order)

1. Hypothesis: FlowProbe::ReportLastRx subtracts a Tx timestamp that is recorded after the Rx time for flow 3, so the delay sum goes negative. Why: only flow 3 is affected and it is the only flow with a reordered first packet.
2. Source: src/flow-monitor/model/flow-probe.cc, ReportLastRx(), the line `delayInNs = Simulator::Now() - txTime` with `txTime` read from the per-packet tag; the tag is overwritten when a packet is forwarded twice. ns-3.43 only.
3. Reproduce: command `./ns3 run manet-12 -- --seed=3`; result under ns-3.43: `flow 3 delaySum=-1.20e+10ns`; under ns-3.42: `flow 3 delaySum=+4.46e+10ns`.
4. Duplicate search: searched ns-3's GitLab issues for "FlowMonitor negative delay" and our sim-tools tickets for NS3-; no hit.
