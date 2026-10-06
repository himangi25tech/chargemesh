# Plan

Build the explanation first. Touch a charger only after a site says yes in writing.

## Why this shape

The original Muse gadget already splits the work. An ESP32 can show text. A Linux gadget can run a local command. Neither one is an optimizer, and neither one should be, because the chat path can be down.

So the first product is a local recommendation the gadget can read. Not a new Muse command on the persona branch. Not an order. Not a VPN hop from a laptop to a board.

## Phases

| Phase | Ships | Does not ship |
| --- | --- | --- |
| 0. This repo | Verdict, architecture, toy estimate | A charger client |
| 1. Linux command | `energy.status` and `energy.ask` read a local JSON file and return text | A write to an EVSE |
| 2. Board | The same text on an ESP32 screen | Spoken replies |
| 3. Meters | Solar and building replace the constants in the toy | A claimed CO2 saving |
| 4. Confirmed profile | A named EVSE, written site permission, then an OCPP profile the EVSE may refuse | V2G, payments, autonomous power |

Phase 1 uses the original gadget SDK command table, the one that existed before the persona commits. The command ignores any path argument and reads one fixed file, the same way a gadget command should not be pointed at another account's files.

`energy.ask` takes a departure time and a target state of charge. It returns three lines: charge now, wait, overnight. Each line has example cost, example carbon, and whether the car still finishes on time. The person picks. The command does not apply the pick.

## Done when

A person can ask "why is my car slow?" and get an answer from the Pi without Muse cloud in the path. The answer names the site cap, the current setpoint, and the departure. If those three are missing, it says so instead of inventing them.

## Papers, used as method not as a claim

- Gan, Topcu, and Low. Optimal decentralized protocol for electric vehicle charging. IEEE Transactions on Power Systems, 2013. [10.1109/TPWRS.2012.2210288](https://doi.org/10.1109/TPWRS.2012.2210288). Valley filling.
- Van Kriekinge, De Cauwer, Sapountzoglou, Coosemans, and Messagie. Peak shaving and cost minimization using model predictive control for uni- and bi-directional charging of electric vehicles. Energy Reports, 2021. [10.1016/j.egyr.2021.11.207](https://doi.org/10.1016/j.egyr.2021.11.207). The later controller shape: forecast, then receding horizon. This repo does not run that controller.
- Open Charge Alliance, OCPP 2.0.1 smart charging. The phase 4 actuator, not phase 1.

Skipped: V2G, a carbon-intensity feed, and a second gadget in the kitchen. Add those when a site has the meter and the permission. The evening toy below has no solar left to use, so a renewable claim would be false.
