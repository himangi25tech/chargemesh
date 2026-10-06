#!/usr/bin/env python3
"""Toy evening estimate. Prints numbers. Does not talk to a charger."""

from __future__ import annotations

import json
from pathlib import Path

DT = 0.25
START = 18 * 4
SLOTS = 13 * 4  # 18:00 to 07:00
LIMIT = 180.0


def hour_of(slot: int) -> float:
    return ((START + slot) % 96) / 4


def price(slot: int) -> float:
    hour = hour_of(slot)
    if 18 <= hour < 22:
        return 8.0
    if hour >= 22 or hour < 6:
        return 4.0
    return 6.0


def carbon(slot: int) -> float:
    hour = hour_of(slot)
    if 18 <= hour < 22:
        return 0.72
    if hour >= 22 or hour < 6:
        return 0.45
    return 0.55


def cars(count: int, ac_kwh: float, pmax: float) -> list[dict]:
    return [
        {
            "name": f"EV-{i + 1}",
            "arrive": 0,
            "depart": SLOTS,
            "ac_kwh": ac_kwh,
            "pmax": pmax,
        }
        for i in range(count)
    ]


def summarize(ev: list[float], building: list[float], solar: list[float], unmet: float) -> dict:
    grid = [building[t] + ev[t] - solar[t] for t in range(SLOTS)]
    peak = max(grid)
    return {
        "peak_grid_kw": round(peak, 1),
        "overload_kw": round(max(0.0, peak - LIMIT), 1),
        "ev_ac_kwh": round(sum(ev) * DT, 1),
        "unmet_ac_kwh": round(unmet, 1),
        "ev_cost_inr": round(sum(price(t) * ev[t] * DT for t in range(SLOTS))),
        "ev_co2_kg": round(sum(carbon(t) * ev[t] * DT for t in range(SLOTS)), 1),
        "solar_to_ev_kwh": round(sum(min(solar[t], ev[t]) * DT for t in range(SLOTS)), 1),
        "on_time": unmet < 0.05,
    }


def uncontrolled(fleet: list[dict], building: list[float], solar: list[float]) -> dict:
    ev = [0.0] * SLOTS
    unmet = 0.0
    for car in fleet:
        left = car["ac_kwh"]
        for t in range(car["arrive"], car["depart"]):
            if left <= 1e-9:
                break
            take = min(car["pmax"], left / DT)
            ev[t] += take
            left -= take * DT
        unmet += max(0.0, left)
    return summarize(ev, building, solar, unmet)


def optimized(fleet: list[dict], building: list[float], solar: list[float]) -> dict:
    power = [[0.0] * SLOTS for _ in fleet]
    unmet = 0.0
    # ponytail: greedy lowest-slot fill, not MPC. Swap in a forecast solver when a meter feed exists.
    order = sorted(range(len(fleet)), key=lambda i: fleet[i]["depart"])
    for i in order:
        car = fleet[i]
        left = car["ac_kwh"]
        while left > 1e-6:
            best = None
            best_key = None
            for t in range(car["arrive"], car["depart"]):
                others = sum(power[j][t] for j in range(len(fleet)))
                grid_now = building[t] + others - solar[t]
                room = min(car["pmax"] - power[i][t], LIMIT - grid_now)
                if room <= 1e-9:
                    continue
                key = (grid_now, price(t), t)
                if best_key is None or key < best_key:
                    best_key = key
                    best = t
            if best is None:
                break
            others = sum(power[j][best] for j in range(len(fleet)))
            room = min(
                car["pmax"] - power[i][best],
                LIMIT - (building[best] + others - solar[best]),
                left / DT,
            )
            power[i][best] += room
            left -= room * DT
        unmet += max(0.0, left)
    ev = [sum(power[i][t] for i in range(len(fleet))) for t in range(SLOTS)]
    return summarize(ev, building, solar, unmet)


def run() -> dict:
    # 24 kWh into the battery at 90% efficiency is 26.667 kWh from the plug.
    fleet = cars(20, ac_kwh=24 / 0.9, pmax=7.0)
    building = [100.0] * SLOTS
    solar = [0.0] * SLOTS
    base = uncontrolled(fleet, building, solar)
    opt = optimized(fleet, building, solar)
    if base["peak_grid_kw"] != 240.0:
        raise SystemExit(f"baseline peak drifted: {base['peak_grid_kw']}")
    if opt["peak_grid_kw"] > LIMIT or not opt["on_time"]:
        raise SystemExit(f"optimized plan missed the cap or a car: {opt}")
    if opt["ev_cost_inr"] >= base["ev_cost_inr"]:
        raise SystemExit("optimized plan did not cut the example bill")
    return {
        "label": "toy evening, not a measured site",
        "inputs": {
            "cars": 20,
            "battery_kwh_each": 24,
            "efficiency": 0.9,
            "plug_kw_max": 7,
            "arrive": "18:00",
            "depart": "07:00",
            "building_kw": 100,
            "solar_kw": 0,
            "site_limit_kw": LIMIT,
            "price_inr_per_kwh": {"18:00-22:00": 8, "22:00-06:00": 4, "06:00-07:00": 6},
            "carbon_kg_per_kwh": {"18:00-22:00": 0.72, "22:00-06:00": 0.45, "06:00-07:00": 0.55},
        },
        "uncontrolled": base,
        "spread": opt,
    }


def main() -> None:
    result = run()
    text = json.dumps(result, indent=2)
    print(text)
    Path(__file__).with_name("result.json").write_text(text + "\n")


if __name__ == "__main__":
    main()
