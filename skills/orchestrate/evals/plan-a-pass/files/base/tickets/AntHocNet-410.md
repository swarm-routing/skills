# swarm-routing/AntHocNet#410 fix(adapter): route table not cleared on interface down

Labels: bug, adapter, model:sonnet-5.5, priority:P1, release:v1.5.0. Open.

## Acceptance criteria

- [ ] a reproducing test: interface down leaves no route through it
- [ ] the adapter clears the routes on `NotifyInterfaceDown`
- [ ] `make check` green

## Depends on

none
