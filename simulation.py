#!/usr/bin/env python3
"""
Mindanawa Disaster Informatics Lab - Iligan City, Philippines
============================================================
Iligan Flood Evacuation & Disaster Response Simulation Engine
============================================================
This production-grade script replicates the complete mathematical model,
urban hydrology algorithms, flood risk analytics, Dijkstra route planners,
and multi-agent search-and-rescue loops implemented in the React application.

Perfect for command-line simulations, Python notebooks, and standalone runs.
"""

import math
import random
import sys
import time
import heapq
from typing import Dict, List, Optional, Tuple, Any

# ==========================================
# 1. CONSTANTS & SYSTEM CONFIGURATION
# ==========================================

INITIAL_BARANGAYS = [
    {"id": "B1", "name": "Hinaplanon", "x": 62.0, "y": 16.0, "elevation": 7, "population": 15400, "riverSourceProximity": "Mandulog"},
    {"id": "B2", "name": "Santiago", "x": 38.0, "y": 18.0, "elevation": 5, "population": 10200, "riverSourceProximity": "Mandulog"},
    {"id": "B3", "name": "Poblacion", "x": 28.0, "y": 30.0, "elevation": 4, "population": 8900, "riverSourceProximity": "Coastal"},
    {"id": "B4", "name": "Tibanga", "x": 48.0, "y": 26.0, "elevation": 22, "population": 12500, "riverSourceProximity": "Safe"},
    {"id": "B5", "name": "Del Carmen", "x": 78.0, "y": 28.0, "elevation": 65, "population": 14100, "riverSourceProximity": "Safe"},
    {"id": "B6", "name": "Pala-o", "x": 42.0, "y": 36.0, "elevation": 11, "population": 16300, "riverSourceProximity": "None"},
    {"id": "B7", "name": "Tubod", "x": 30.0, "y": 43.0, "elevation": 8, "population": 13800, "riverSourceProximity": "Agus"},
    {"id": "B8", "name": "Ubaldo Laya", "x": 58.0, "y": 42.0, "elevation": 15, "population": 11000, "riverSourceProximity": "None"},
    {"id": "B9", "name": "Mahayahay", "x": 46.0, "y": 32.0, "elevation": 13, "population": 9200, "riverSourceProximity": "None"},
    {"id": "B10", "name": "San Roque", "x": 82.0, "y": 14.0, "elevation": 18, "population": 7600, "riverSourceProximity": "Mandulog"},
    {"id": "B11", "name": "Ditucalan", "x": 86.0, "y": 48.0, "elevation": 120, "population": 4500, "riverSourceProximity": "Agus"},
    {"id": "B12", "name": "Ma. Cristina", "x": 75.0, "y": 54.0, "elevation": 150, "population": 5200, "riverSourceProximity": "Safe"}
]

INITIAL_ROADS = [
    {"id": "R1", "name": "Mandulog Bridge (Hwy)", "from": "B1", "to": "B2", "distance": 1.2, "isBridge": True, "baselineElevation": 6},
    {"id": "R2", "name": "Santiago-Tibanga Road", "from": "B2", "to": "B4", "distance": 1.5, "isBridge": False, "baselineElevation": 12},
    {"id": "R3", "name": "Tibanga-Poblacion Highway", "from": "B4", "to": "B3", "distance": 1.8, "isBridge": False, "baselineElevation": 11},
    {"id": "R4", "name": "Poblacion-Palao Link", "from": "B3", "to": "B6", "distance": 1.0, "isBridge": False, "baselineElevation": 8},
    {"id": "R5", "name": "Palao-Mahayahay Avenue", "from": "B6", "to": "B9", "distance": 0.8, "isBridge": False, "baselineElevation": 12},
    {"id": "R6", "name": "Agus River Tubod Bridge", "from": "B6", "to": "B7", "distance": 2.2, "isBridge": True, "baselineElevation": 7},
    {"id": "R7", "name": "Tibanga-Del Carmen Trunk", "from": "B4", "to": "B5", "distance": 2.8, "isBridge": False, "baselineElevation": 40},
    {"id": "R8", "name": "Hinaplanon-San Roque Boulevard", "from": "B1", "to": "B10", "distance": 3.1, "isBridge": False, "baselineElevation": 12},
    {"id": "R9", "name": "Del Carmen Spine Rd", "from": "B5", "to": "B8", "distance": 2.5, "isBridge": False, "baselineElevation": 35},
    {"id": "R10", "name": "Mahayahay-Laya Link", "from": "B9", "to": "B8", "distance": 1.3, "isBridge": False, "baselineElevation": 14},
    {"id": "R11", "name": "Upper Mandulog Bypass Bridge", "from": "B10", "to": "B5", "distance": 4.2, "isBridge": True, "baselineElevation": 35},
    {"id": "R12", "name": "Tubod-Ditucalan Riverside Road", "from": "B7", "to": "B11", "distance": 5.6, "isBridge": False, "baselineElevation": 45},
    {"id": "R13", "name": "Ditucalan Cascade Road", "from": "B11", "to": "B12", "distance": 3.5, "isBridge": False, "baselineElevation": 135},
    {"id": "R14", "name": "Poblacion-Mahayahay Bypass", "from": "B3", "to": "B9", "distance": 0.7, "isBridge": False, "baselineElevation": 9},
    {"id": "R15", "name": "Laya-Tubod Access Road", "from": "B8", "to": "B7", "distance": 1.6, "isBridge": False, "baselineElevation": 11}
]

INITIAL_EVAC_CENTERS = [
    {"id": "EC1", "name": "MSU-IIT Gymnasium", "barangayId": "B4", "capacity": 1500, "occupancy": 0, "elevation": 45, "x": 48.0, "y": 24.0, "isAvailable": True},
    {"id": "EC2", "name": "City Hall Annex / Anahaw Amphitheater", "barangayId": "B6", "capacity": 2500, "occupancy": 0, "elevation": 80, "x": 41.0, "y": 38.0, "isAvailable": True},
    {"id": "EC3", "name": "Del Carmen Multi-Purpose Gym", "barangayId": "B5", "capacity": 1200, "occupancy": 0, "elevation": 65, "x": 78.0, "y": 26.0, "isAvailable": True},
    {"id": "EC4", "name": "Maria Cristina Covered Court", "barangayId": "B12", "capacity": 600, "occupancy": 0, "elevation": 150, "x": 75.0, "y": 52.0, "isAvailable": True},
    {"id": "EC5", "name": "Tubod Brgy Gymnasium", "barangayId": "B7", "capacity": 800, "occupancy": 0, "elevation": 12, "x": 30.0, "y": 45.0, "isAvailable": True},
    {"id": "EC6", "name": "Hinaplanon Central School Gym", "barangayId": "B1", "capacity": 700, "occupancy": 0, "elevation": 8, "x": 62.0, "y": 14.0, "isAvailable": True}
]

# Scenario Parameters corresponding to simulation presets
SCENARIOS = {
    "TS Basyang": {
        "rainfall": 180,
        "tideLevel": 1.8,
        "drainageCapacity": 65,
        "bridgeFailure": True,
        "crowdingFactor": 1.5,
        "initialPopulation": 450,
        "activeScenarioName": "TS Basyang"
    },
    "Super Typhoon": {
        "rainfall": 280,
        "tideLevel": 2.5,
        "drainageCapacity": 40,
        "bridgeFailure": True,
        "crowdingFactor": 2.0,
        "initialPopulation": 750,
        "activeScenarioName": "Super Typhoon"
    },
    "High Tide Flash Flood": {
        "rainfall": 140,
        "tideLevel": 2.8,
        "drainageCapacity": 50,
        "bridgeFailure": False,
        "crowdingFactor": 1.2,
        "initialPopulation": 350,
        "activeScenarioName": "High Tide Flash Flood"
    },
    "Default": {
        "rainfall": 90,
        "tideLevel": 0.5,
        "drainageCapacity": 85,
        "bridgeFailure": False,
        "crowdingFactor": 1.0,
        "initialPopulation": 250,
        "activeScenarioName": "Default"
    }
}

# ==========================================
# 2. HYDROLOGICAL AND SIMULATION FUNCTIONS
# ==========================================

def calculate_flood_depth(barangay: Dict[str, Any], state: Dict[str, Any], random_noise: float = 0.0) -> float:
    """
    Evaluates physical flood elevations based on local river proximity, tide height,
    rain intensity, drainage health, and crisis elapsed hours.
    """
    rainfall = state["rainfall"]
    tide_level = state["tideLevel"]
    drainage_capacity = state["drainageCapacity"]
    current_time = state["currentTime"]
    bridge_failure = state["bridgeFailure"]

    base_depth = 0.0
    river_proximity = barangay["riverSourceProximity"]
    elevation = barangay["elevation"]

    if river_proximity == "Mandulog":
        swell = (rainfall / 100.0) * 1.5 * (current_time / 3.0)
        bridge_impact = 0.8 if bridge_failure else 0.0
        base_depth = max(0.0, swell + bridge_impact - elevation * 0.12)
    elif river_proximity == "Agus":
        swell = (rainfall / 100.0) * 1.0 * (current_time / 4.0)
        base_depth = max(0.0, swell - elevation * 0.1)
    elif river_proximity == "Coastal":
        coastal_impact = max(0.0, tide_level * 0.8) + (rainfall / 150.0)
        base_depth = max(0.0, coastal_impact * (1.0 + current_time * 0.1) - elevation * 0.15)
    elif river_proximity == "None":
        accumulation = (rainfall / 150.0) * 0.8 * (current_time / 2.0)
        drainage_mitigation = drainage_capacity / 100.0
        base_depth = max(0.0, accumulation * (1.1 - drainage_mitigation) - elevation * 0.08)
    else:
        base_depth = 0.0

    # Curve mapping peaked around hour 4.5-5.0
    time_curve = min(1.0, current_time / 4.5)
    base_depth *= time_curve
    base_depth = max(0.0, base_depth + random_noise)

    return round(base_depth, 2)


def run_monte_carlo(state: Dict[str, Any], iterations: int = 100) -> Dict[str, Any]:
    """
    Runs multi-pass perturbation testing over the model variables to establish
    probabilistic flood vulnerability scores for each node and roadway.
    """
    brgy_counts = {b["id"]: 0 for b in INITIAL_BARANGAYS}
    depth_totals = {b["id"]: 0.0 for b in INITIAL_BARANGAYS}
    road_counts = {r["id"]: 0 for r in INITIAL_ROADS}
    bridge_collapse_count = 0

    for _ in range(iterations):
        noise_rain = state["rainfall"] * (0.85 + random.random() * 0.3)  # +/- 15%
        noise_tide = state["tideLevel"] + (random.random() * 0.6 - 0.3)  # +/- 0.3m
        noise_drain = max(0.0, min(100.0, state["drainageCapacity"] * (0.8 + random.random() * 0.4)))
        temp_bridge_fail = state["bridgeFailure"] or (noise_rain > 220 and random.random() > 0.4)

        if temp_bridge_fail:
            bridge_collapse_count += 1

        iter_state = {
            "rainfall": noise_rain,
            "tideLevel": noise_tide,
            "drainageCapacity": noise_drain,
            "bridgeFailure": temp_bridge_fail,
            "currentTime": state["currentTime"]
        }

        # Evaluate mock Brgy states
        iter_bounds = {}
        for b in INITIAL_BARANGAYS:
            local_noise = (random.random() - 0.5) * 0.2
            depth = calculate_flood_depth(b, iter_state, local_noise)
            iter_bounds[b["id"]] = depth
            depth_totals[b["id"]] += depth
            if depth >= 0.3:
                brgy_counts[b["id"]] += 1

        # Evaluate Road passability
        for r in INITIAL_ROADS:
            from_depth = iter_bounds[r["from"]]
            to_depth = iter_bounds[r["to"]]
            avg_depth = (from_depth + to_depth) / 2.0

            is_blocked = False
            if avg_depth > 0.4:
                is_blocked = True
            if r["isBridge"] and temp_bridge_fail:
                swell_prox = next((bg["riverSourceProximity"] for bg in INITIAL_BARANGAYS if bg["id"] == r["from"]), "None")
                if swell_prox == "Mandulog" and noise_rain > 150:
                    is_blocked = True
            
            debris_prob = (noise_rain / 300.0) * 0.08
            if random.random() < debris_prob:
                is_blocked = True

            if not is_blocked:
                road_counts[r["id"]] += 1

    brgy_probs = {key: val / iterations for key, val in brgy_counts.items()}
    avg_depths = {key: round(val / iterations, 2) for key, val in depth_totals.items()}
    road_pass = {key: val / iterations for key, val in road_counts.items()}

    return {
        "runCount": iterations,
        "barangayFloodProb": brgy_probs,
        "roadPassabilityProb": road_pass,
        "averageDepths": avg_depths,
    }


# ==========================================
# 3. PATHFINDING DIJKSTRA ROUTE PLANNER
# ==========================================

def find_safe_route(
    start_brgy_id: str,
    end_center_id: str,
    roads: List[Dict[str, Any]],
    barangays: List[Dict[str, Any]],
    mc_results: Dict[str, Any],
    state: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Computes a dynamically weighted Dijkstra shortest path back to target safe zones,
    factoring in water depths, bridge failures, and crowd densities using a Priority Queue.
    """
    center = next((c for c in INITIAL_EVAC_CENTERS if c["id"] == end_center_id), None)
    target_brgy_id = center["barangayId"] if center else ""

    if start_brgy_id == target_brgy_id:
        return {
            "routePath": [start_brgy_id],
            "isSafe": True,
            "riskScore": 0,
            "estimatedTimeMin": 0,
            "reasons": ["Already inside target safe zone evacuation center."]
        }

    # Dijkstra arrays
    distances = {b["id"]: float("inf") for b in barangays}
    previous = {b["id"]: None for b in barangays}
    distances[start_brgy_id] = 0.0

    pq = [(0.0, start_brgy_id)]
    visited = set()

    while len(pq) > 0:
        current_dist, u = heapq.heappop(pq)

        if u == target_brgy_id:
            break
        if u in visited:
            continue
        visited.add(u)

        # Seek roads connecting node u
        connecting_segments = [
            r for r in roads if r["from"] == u or r["to"] == u
        ]

        for road in connecting_segments:
            neighbor = road["to"] if road["from"] == u else road["from"]
            if neighbor in visited:
                continue

            prob = mc_results["roadPassabilityProb"].get(road["id"], 1.0)
            road_depth = road.get("currentDepth", 0.0)
            is_failed_bridge = state["bridgeFailure"] and road["isBridge"]

            # EQUATION 1: Quadratic Depth Penalty
            alpha = 25.0
            beta = 50.0
            risk_penalty = 1.0
            
            if road_depth > 0.4:
                risk_penalty += alpha * (road_depth ** 2)
            if prob < 0.8:
                risk_penalty += beta * (1.0 - prob)
            if is_failed_bridge:
                risk_penalty += 10000.0  # Impassable barrier

            alt_dist = current_dist + (road["distance"] * risk_penalty)
            if alt_dist < distances[neighbor]:
                distances[neighbor] = alt_dist
                previous[neighbor] = u
                heapq.heappush(pq, (alt_dist, neighbor))

    # Trace backward paths
    path = []
    curr = target_brgy_id
    while curr:
        path.insert(0, curr)
        curr = previous[curr]

    if not path or path[0] != start_brgy_id:
        return {
            "routePath": [],
            "isSafe": False,
            "riskScore": 100,
            "estimatedTimeMin": float("inf"),
            "reasons": ["No topo-safe paths above sea/river swelling thresholds. Evacuate upland!"]
        }

    # Time parameters estimation
    total_dist = 0.0
    total_fail_rate = 0.0
    for j in range(len(path) - 1):
        u_node, v_node = path[j], path[j+1]
        seg = next((r for r in roads if (r["from"] == u_node and r["to"] == v_node) or (r["from"] == v_node and r["to"] == u_node)), None)
        if seg:
            total_dist += seg["distance"]
            total_fail_rate += (1.0 - mc_results["roadPassabilityProb"].get(seg["id"], 1.0))

    base_speed = 4.0  # walking km/h
    start_depth = next((b["floodDepth"] for b in barangays if b["id"] == start_brgy_id), 0.0)
    slowfactor = max(0.1, 1.0 - start_depth * 1.5)
    est_time = round((total_dist / (base_speed * slowfactor)) * 60)

    agg_risk = min(100, round((total_fail_rate / max(1, len(path)-1)) * 50 + (start_depth * 35)))

    return {
        "routePath": path,
        "isSafe": agg_risk < 50,
        "riskScore": agg_risk,
        "estimatedTimeMin": est_time,
        "reasons": ["Dynamic shortest-path computed with hydrology weights."]
    }


# ==========================================
# 4. CHRONO MULTI-AGENT RESCUE SIMULATOR
# ==========================================

def run_discrete_hour_simulation(scenario_name: str) -> Dict[str, Any]:
    """
    Executes a high-fidelity hour-by-hour local simulation of the chosen disaster
    scenario, mirroring the exact state progress and CDRRMC SAR dispatching logic.
    """
    print(f"\n=======================================================")
    print(f"ILIGAN ENGINE CORE: INITIATING FULL {scenario_name.upper()} RUN")
    print(f"=======================================================\n")

    conf = SCENARIOS[scenario_name]
    state = {**conf, "currentTime": 0.0}

    # Copy raw data states
    active_barangays = [{**b, "floodDepth": 0.0} for b in INITIAL_BARANGAYS]
    active_roads = [{**r, "currentDepth": 0.0} for r in INITIAL_ROADS]
    active_centers = [{**c, "occupancy": 0} for c in INITIAL_EVAC_CENTERS]

    # Pre-calculate Monte Carlo curves dynamically for path risks
    mc_results = run_monte_carlo(state, 100)

    # Spawn Simulated Civil Agents modeling residential hubs
    print(f"[*] Spawning {conf['initialPopulation']} civilian evacuee agents across vulnerable zones...")
    civilians = []
    flood_prone_brgys = ["B1", "B2", "B3", "B7", "B8", "B9", "B10"]
    
    for i in range(conf["initialPopulation"]):
        source_id = random.choice(flood_prone_brgys)
        target_center = random.choice(["EC1", "EC2", "EC3", "EC5"])
        # Give diverse personal delays (Log-Normal preparation time hours matching Section III-C)
        prep_time = round(0.5 + random.lognormvariate(0.0, 0.5), 2)
        civilians.append({
            "id": f"CIV-{i+1:03d}",
            "sourceBarangayId": source_id,
            "targetCenterId": target_center,
            "currentBarangayId": source_id,
            "status": "Preparing",  # Preparing | Evacuating | Stuck | RescueNeeded | Safe | Casualty
            "prepTimeHours": prep_time,
            "x": 0.0, "y": 0.0,
            "path": [],
            "currentPathIndex": 0
        })

    # Spawn 5 Highly Equipped CDRRMC Search and Rescue (SAR) Units
    print("[*] Dispatching 5 CDRRMC Search and Rescue Specialist Units...")
    rescuers = [
        {"id": "R1", "name": "CDRRMC SAR Squad Alpha", "status": "Idle", "x": 48.0, "y": 24.0, "targetAgentId": None, "targetCenterId": None, "speed": 2.8, "rescuedCount": 0},
        {"id": "R2", "name": "PCG Amphibious Team Bravo", "status": "Idle", "x": 41.0, "y": 38.0, "targetAgentId": None, "targetCenterId": None, "speed": 3.2, "rescuedCount": 0},
        {"id": "R3", "name": "Iligan Red Cross Support Delta", "status": "Idle", "x": 78.0, "y": 26.0, "targetAgentId": None, "targetCenterId": None, "speed": 3.0, "rescuedCount": 0},
        {"id": "R4", "name": "Iligan BFP Rescue Squad Echo", "status": "Idle", "x": 75.0, "y": 52.0, "targetAgentId": None, "targetCenterId": None, "speed": 2.6, "rescuedCount": 0},
        {"id": "R5", "name": "MSU-IIT Student Medical Responders", "status": "Idle", "x": 48.0, "y": 24.0, "targetAgentId": None, "targetCenterId": None, "speed": 2.4, "rescuedCount": 0},
    ]

    time_step = 0.1  # 6-minute simulation step updates
    total_hours = 6.0
    current_time = 0.0

    print("\n-------------------------------------------------------")
    print(f"|  Hour  | Safe (Arrived) | Moving | Stranded | Casualty |")
    print("-------------------------------------------------------")

    while current_time <= total_hours:
        state["currentTime"] = current_time

        # 1. Update hydrological curves for flood depths
        for b in active_barangays:
            b["floodDepth"] = calculate_flood_depth(b, state)

        for road in active_roads:
            d_from = next((bg["floodDepth"] for bg in active_barangays if bg["id"] == road["from"]), 0.0)
            d_to = next((bg["floodDepth"] for bg in active_barangays if bg["id"] == road["to"]), 0.0)
            road["currentDepth"] = round((d_from + d_to) / 2.0, 2)

        # 2. Iterate and step through evacuee actions
        for civ in civilians:
            if civ["status"] == "Safe" or civ["status"] == "Casualty":
                continue

            # a. Delayed preparation phase
            if civ["status"] == "Preparing":
                if current_time >= civ["prepTimeHours"]:
                    # Done prepping, locate best topological route
                    route_info = find_safe_route(
                        civ["sourceBarangayId"],
                        civ["targetCenterId"],
                        active_roads,
                        active_barangays,
                        mc_results,
                        state
                    )
                    if route_info["routePath"] and len(route_info["routePath"]) > 1:
                        civ["path"] = route_info["routePath"]
                        civ["currentPathIndex"] = 0
                        civ["status"] = "Evacuating"
                    else:
                        civ["status"] = "Stuck"  # Blocked from departure

                # Check if preparing in rapidly drowning neighborhoods
                srv_bg = next((bg for bg in active_barangays if bg["id"] == civ["sourceBarangayId"]), None)
                if srv_bg and srv_bg["floodDepth"] > 0.8:
                    if random.random() < 0.005:  # swift flash death hazard
                        civ["status"] = "Casualty"

            # b. Active Route Walking Transit phase
            elif civ["status"] == "Evacuating":
                src_node = civ["path"][civ["currentPathIndex"]]
                next_node = civ["path"][civ["currentPathIndex"] + 1]

                # Identify corresponding road segment
                road_segment = next((r for r in active_roads if (r["from"] == src_node and r["to"] == next_node) or (r["from"] == v_node and r["to"] == u_node)), None)
                active_segment_depth = road_segment["currentDepth"] if road_segment else 0.0

                if active_segment_depth > 0.95:
                    if random.random() < 0.001:  # 0.1% drowning chance per tick in swift flood stream
                        civ["status"] = "Casualty"
                        continue

                # Progress along segment
                civ["currentPathIndex"] += 1
                civ["currentBarangayId"] = next_node

                # Check if reached destination
                dest_center = next((c for c in active_centers if c["id"] == civ["targetCenterId"]), None)
                if next_node == dest_center["barangayId"]:
                    civ["status"] = "Safe"
                    dest_center["occupancy"] += 1
                elif civ["currentPathIndex"] >= len(civ["path"]) - 1:
                    civ["status"] = "Safe"

            # c. Trap status checking
            elif civ["status"] == "Stuck":
                local_bg = next((b for b in active_barangays if b["id"] == civ["currentBarangayId"]), None)
                if local_bg and local_bg["floodDepth"] > 1.2:
                    if random.random() < 0.001:
                        civ["status"] = "Casualty"
                    else:
                        civ["status"] = "RescueNeeded"

        # 3. Handle physical dispatches with the active CDRRMC Rescue Specialists
        for resc in rescuers:
            if resc["status"] == "Idle":
                # Find the nearest stranded/alert civilian
                trapped_civ = next((c for c in civilians if c["status"] in ("RescueNeeded", "Stuck") and not any(r["targetAgentId"] == c["id"] for r in rescuers if r["id"] != resc["id"])), None)
                if trapped_civ:
                    resc["status"] = "Dispatched"
                    resc["targetAgentId"] = trapped_civ["id"]
            
            elif resc["status"] == "Dispatched":
                trapped_civ = next((c for c in civilians if c["id"] == resc["targetAgentId"]), None)
                if not trapped_civ or trapped_civ["status"] in ("Safe", "Casualty"):
                    # Target already lost or resolved
                    resc["status"] = "Idle"
                    resc["targetAgentId"] = None
                    continue

                # Coordinate travel stepping
                tg_bg = next((b for b in active_barangays if b["id"] == trapped_civ["currentBarangayId"]), None)
                if tg_bg:
                    # Relocate to target
                    resc["status"] = "Returning"
                    resc["targetCenterId"] = trapped_civ["targetCenterId"]

            elif resc["status"] == "Returning":
                trapped_civ = next((c for c in civilians if c["id"] == resc["targetAgentId"]), None)
                dest_center = next((c for c in active_centers if c["id"] == resc["targetCenterId"]), active_centers[0])
                
                # Rescuers successfully escorted trainee back to Gym/Shelter
                if trapped_civ:
                    trapped_civ["status"] = "Safe"
                    dest_center["occupancy"] += 1
                
                resc["status"] = "Idle"
                if trapped_civ:
                    resc["rescuedCount"] += 1
                resc["targetAgentId"] = None
                resc["targetCenterId"] = None

        # Count state aggregates
        safe_cnt = sum(1 for c in civilians if c["status"] == "Safe")
        transit_cnt = sum(1 for c in civilians if c["status"] == "Evacuating")
        stranded_cnt = sum(1 for c in civilians if c["status"] in ("Stuck", "RescueNeeded"))
        dead_cnt = sum(1 for c in civilians if c["status"] == "Casualty")

        # Scaled indicators representing raw residential census
        scaled_safe = safe_cnt * 250
        scaled_transit = transit_cnt * 250
        scaled_stranded = stranded_cnt * 250
        scaled_dead = dead_cnt # tracked 1:1 on absolute scale (highly local)

        print(f"| H-{current_time:3.1f} | {scaled_safe:14,d} | {scaled_transit:6,d} | {scaled_stranded:8,d} | {scaled_dead:8d} |")
        
        current_time = round(current_time + time_step, 2)

    print("-------------------------------------------------------")
    print(f"\n[*] Simulation finished at H-6.0.")
    print(f"[+] Protected Residents: {sum(c['occupancy'] for c in active_centers) * 250:,d} citizens.")
    print(f"[+] Total Simulated Deaths: {dead_cnt} cases.")
    print(f"[+] Rescuer Saves:")
    for resc in rescuers:
        print(f"    - {resc['name']}: Saved {resc['rescuedCount'] * 250:,d} residents.")
    
    return {
        "scenario": scenario_name,
        "protected": sum(c['occupancy'] for c in active_centers) * 250,
        "casualties": dead_cnt,
        "rescuers": rescuers
    }


def main():
    print("=====================================================================")
    print("      MINDANAWA DISASTER INFORMATICS LAB - ILIGAN PHP SIMULATOR       ")
    print("=====================================================================")
    
    # Prompt option selectors
    print("Available Simulation Scenarios:")
    for idx, key in enumerate(SCENARIOS.keys(), 1):
        print(f"  {idx}. {key}")
    
    choice = input("\nSelect Scenario to execute (default: 1): ").strip()
    sel_key = "TS Basyang"
    if choice == "2":
        sel_key = "Super Typhoon"
    elif choice == "3":
        sel_key = "High Tide Flash Flood"
    elif choice == "4":
        sel_key = "Default"

    run_discrete_hour_simulation(sel_key)


if __name__ == "__main__":
    main()