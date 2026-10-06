# ChargeMesh

A plan for a community EV charging assistant that uses a Muse gadget as the face. The gadget does not switch the charger.

This repo is not a patch on [muse-gadget-sdk](https://github.com/facebookincubator/muse-gadget-sdk) and not a branch of `muse-client`. It is the original gadget split: a person talks to Muse, a Linux box holds the plan. The persona-notes branch is a different product.

## Verdict

Yes, as a face. No, as a brain.

The useful Muse moment is a person at the charger asking when the car will be ready, and hearing why it is slow. That fits a gadget with a screen and a Linux command. The schedule itself is an old problem: valley filling (Gan, Topcu, and Low, 2013) and MPC peak shaving (Van Kriekinge et al., 2021). Muse does not make that math new.

Do not put the control loop in Muse cloud. A board in India that can reach Muse only through a laptop VPN must not be the thing that decides kilowatts. The Pi keeps the last safe recommendation if Muse is unreachable.

v1 stops at a recommendation. An EVSE or BMS is the only thing that may apply power, and it can refuse.

## In this repo

| Doc | What it answers |
| --- | --- |
| [docs/plan.md](docs/plan.md) | What to build, in order |
| [docs/architecture.md](docs/architecture.md) | Who talks to whom |
| [docs/estimate.md](docs/estimate.md) | Inputs, outputs, and the toy numbers |

```sh
python3 sim/estimate.py
```

That writes `sim/result.json`. It does not open a socket.

Unofficial. Not affiliated with Meta. Not a grid controller.
