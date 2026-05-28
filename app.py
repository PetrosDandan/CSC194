#!/usr/bin/env python3
"""
MINDANAWA DISASTER INFORMATICS LAB - ILIGAN CITY, PHILIPPINES
==============================================================
Iligan Flood Evacuation, CDRRMC SAR Patrol, & Situational-Awareness Engine
==============================================================
A 100% pure Python full-stack interactive web application serving high-performance
simulation control systems on port 3000. Uses only standard, built-in Python libraries.
"""

import http.server
import socketserver
import json
import math
import random
import sys
import threading
import urllib.parse
from typing import Dict, List, Optional, Tuple, Any

# ==========================================
# 1. CORE DATA & PHYSICAL BASELINES
# ==========================================

INITIAL_BARANGAYS = [
    {"id": "B1", "name": "Hinaplanon", "x": 620, "y": 120, "lat": 8.2467, "lng": 124.2658, "elevation": 7, "population": 15400, "riverSourceProximity": "Mandulog"},
    {"id": "B2", "name": "Santiago", "x": 380, "y": 140, "lat": 8.2435, "lng": 124.2541, "elevation": 5, "population": 10200, "riverSourceProximity": "Mandulog"},
    {"id": "B3", "name": "Poblacion", "x": 280, "y": 280, "lat": 8.2281, "lng": 124.2403, "elevation": 4, "population": 8900, "riverSourceProximity": "Coastal"},
    {"id": "B4", "name": "Tibanga", "x": 480, "y": 230, "lat": 8.2407, "lng": 124.2439, "elevation": 22, "population": 12500, "riverSourceProximity": "Safe"},
    {"id": "B5", "name": "Del Carmen", "x": 780, "y": 250, "lat": 8.2323, "lng": 124.2694, "elevation": 65, "population": 14100, "riverSourceProximity": "Safe"},
    {"id": "B6", "name": "Pala-o", "x": 420, "y": 340, "lat": 8.2198, "lng": 124.2443, "elevation": 11, "population": 16300, "riverSourceProximity": "None"},
    {"id": "B7", "name": "Tubod", "x": 300, "y": 440, "lat": 8.2144, "lng": 124.2346, "elevation": 8, "population": 13800, "riverSourceProximity": "Agus"},
    {"id": "B8", "name": "Ubaldo Laya", "x": 580, "y": 420, "lat": 8.2166, "lng": 124.2559, "elevation": 15, "population": 11000, "riverSourceProximity": "None"},
    {"id": "B9", "name": "Mahayahay", "x": 460, "y": 300, "lat": 8.2259, "lng": 124.2514, "elevation": 13, "population": 9200, "riverSourceProximity": "None"},
    {"id": "B10", "name": "San Roque", "x": 820, "y": 90, "lat": 8.2713, "lng": 124.2831, "elevation": 18, "population": 7600, "riverSourceProximity": "Mandulog"},
    {"id": "B11", "name": "Ditucalan", "x": 860, "y": 470, "lat": 8.1883, "lng": 124.2444, "elevation": 120, "population": 4500, "riverSourceProximity": "Agus"},
    {"id": "B12", "name": "Ma. Cristina", "x": 750, "y": 530, "lat": 8.1812, "lng": 124.1950, "elevation": 150, "population": 5200, "riverSourceProximity": "Safe"}
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
    {"id": "EC1", "name": "MSU-IIT Gymnasium", "barangayId": "B4", "capacity": 1500, "occupancy": 0, "elevation": 45, "x": 480, "y": 210, "lat": 8.2415, "lng": 124.2443, "isAvailable": True},
    {"id": "EC2", "name": "City Hall Annex / Anahaw Amphitheater", "barangayId": "B6", "capacity": 2500, "occupancy": 0, "elevation": 80, "x": 410, "y": 360, "lat": 8.2198, "lng": 124.2443, "isAvailable": True},
    {"id": "EC3", "name": "Del Carmen Multi-Purpose Gym", "barangayId": "B5", "capacity": 1200, "occupancy": 0, "elevation": 65, "x": 780, "y": 230, "lat": 8.2323, "lng": 124.2694, "isAvailable": True},
    {"id": "EC4", "name": "Maria Cristina Covered Court", "barangayId": "B12", "capacity": 600, "occupancy": 0, "elevation": 150, "x": 750, "y": 510, "lat": 8.1812, "lng": 124.1950, "isAvailable": True},
    {"id": "EC5", "name": "Tubod Brgy Gymnasium", "barangayId": "B7", "capacity": 800, "occupancy": 0, "elevation": 12, "x": 300, "y": 420, "lat": 8.2144, "lng": 124.2346, "isAvailable": True},
    {"id": "EC6", "name": "Hinaplanon Central School Gym", "barangayId": "B1", "capacity": 700, "occupancy": 0, "elevation": 8, "x": 620, "y": 100, "lat": 8.2467, "lng": 124.2658, "isAvailable": True}
]

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
# 2. STATE CO-ORDINATOR ENGINE
# ==========================================

class SimulationEngine:
    def __init__(self):
        self.lock = threading.Lock()
        self.reset("TS Basyang")

    def reset(self, scenario_name="Default"):
        with self.lock:
            self.scenario_name = scenario_name
            self.current_time = 0.0
            self.is_running = False
            self.cached_mc = None
            self.cached_mc_inputs = None
            
            conf = SCENARIOS.get(scenario_name, SCENARIOS["Default"])
            self.rainfall = conf["rainfall"]
            self.tide_level = conf["tideLevel"]
            self.drainage_capacity = conf["drainageCapacity"]
            self.bridge_failure = conf["bridgeFailure"]
            self.crowding_factor = conf["crowdingFactor"]
            self.initial_population = conf["initialPopulation"]
            
            self.barangays = [dict(b) for b in INITIAL_BARANGAYS]
            self.roads = [dict(r) for r in INITIAL_ROADS]
            self.centers = [dict(c) for c in INITIAL_EVAC_CENTERS]
            
            for b in self.barangays:
                b["floodDepth"] = 0.0
                b["floodProb"] = 0.0
                b["status"] = "Safe"
                
            for r in self.roads:
                r["currentDepth"] = 0.0
                r["passabilityProb"] = 1.0
                r["status"] = "Safe"

            # Create physical agent list (scaled)
            self.agents = []
            flood_prone = ["B1", "B2", "B3", "B7", "B8", "B9", "B10"]
            for i in range(self.initial_population):
                source = random.choice(flood_prone)
                target = random.choice(["EC1", "EC2", "EC3", "EC5"])
                # personal layout delays
                prep_hrs = round(0.5 + random.random() * 1.8, 2)
                self.agents.append({
                    "id": f"CIV-{i+1:03d}",
                    "sourceBarangayId": source,
                    "targetCenterId": target,
                    "currentBarangayId": source,
                    "status": "Preparing",  # Preparing, Evacuating, Stuck, RescueNeeded, Safe, Casualty
                    "prepTimeHours": prep_hrs,
                    "path": [],
                    "currentPathIndex": 0
                })

            # Rescuers Specialist Fleet
            self.rescuers = [
                {"id": "R1", "name": "CDRRMC SAR Squad Alpha", "status": "Idle", "targetAgentId": None, "targetCenterId": None, "speed": 2.8, "rescuedCount": 0, "barangayId": "B4", "path": [], "currentPathIndex": 0},
                {"id": "R2", "name": "PCG Amphibious Team Bravo", "status": "Idle", "targetAgentId": None, "targetCenterId": None, "speed": 3.2, "rescuedCount": 0, "barangayId": "B6", "path": [], "currentPathIndex": 0},
                {"id": "R3", "name": "Iligan Red Cross Support Delta", "status": "Idle", "targetAgentId": None, "targetCenterId": None, "speed": 3.0, "rescuedCount": 0, "barangayId": "B5", "path": [], "currentPathIndex": 0},
                {"id": "R4", "name": "Iligan BFP Rescue Squad Echo", "status": "Idle", "targetAgentId": None, "targetCenterId": None, "speed": 2.6, "rescuedCount": 0, "barangayId": "B12", "path": [], "currentPathIndex": 0},
                {"id": "R5", "name": "MSU-IIT Student Medical Responders", "status": "Idle", "targetAgentId": None, "targetCenterId": None, "speed": 2.4, "rescuedCount": 0, "barangayId": "B4", "path": [], "currentPathIndex": 0},
            ]
            
            self.update_hydrology()
            self.history = []
            mc = self.run_monte_carlo()
            self.record_history_step(mc)

    def update_hydrology(self):
        # Calculate instant flood levels
        for b in self.barangays:
            b["floodDepth"] = self.calculate_brgy_depth(b)
            
        for r in self.roads:
            d_from = next((b["floodDepth"] for b in self.barangays if b["id"] == r["from"]), 0.0)
            d_to = next((b["floodDepth"] for b in self.barangays if b["id"] == r["to"]), 0.0)
            avg_d = round((d_from + d_to) / 2.0, 2)
            
            # blocked limit
            if r["isBridge"] and self.bridge_failure and r["from"] in ("B1", "B10") and self.rainfall > 150:
                r["currentDepth"] = max(1.8, avg_d)
                r["status"] = "Closed"
            else:
                r["currentDepth"] = avg_d
                r["status"] = "Safe" if avg_d < 0.4 else ("Flooded" if avg_d < 0.8 else "Blocked")

    def record_history_step(self, mc):
        stats = {
            "time": self.current_time,
            "safeCount": sum(1 for a in self.agents if a["status"] == "Safe"),
            "casualtyCount": sum(1 for a in self.agents if a["status"] == "Casualty"),
            "evacuatingCount": sum(1 for a in self.agents if a["status"] == "Evacuating"),
            "preparingCount": sum(1 for a in self.agents if a["status"] == "Preparing"),
            "stuckCount": sum(1 for a in self.agents if a["status"] in ("Stuck", "RescueNeeded")),
            "barangayDepths": {b["id"]: b["floodDepth"] for b in self.barangays},
            "barangayProbs": {b["id"]: mc["barangayFloodProb"].get(b["id"], 0.0) for b in self.barangays}
        }
        # Prevent duplicates
        self.history = [h for h in self.history if h["time"] < self.current_time]
        self.history.append(stats)

    def calculate_brgy_depth(self, b: Dict[str, Any], state_override: Optional[Dict[str, Any]] = None) -> float:
        rain = state_override["rainfall"] if state_override else self.rainfall
        tide = state_override["tideLevel"] if state_override else self.tide_level
        drain = state_override["drainageCapacity"] if state_override else self.drainage_capacity
        hrs = state_override["currentTime"] if state_override else self.current_time
        b_fail = state_override["bridgeFailure"] if state_override else self.bridge_failure

        river = b["riverSourceProximity"]
        el = b["elevation"]
        base_depth = 0.0

        if river == "Mandulog":
            swell = (rain / 100.0) * 1.5 * (hrs / 3.0)
            bridge_factor = 0.8 if b_fail else 0.0
            base_depth = max(0.0, swell + bridge_factor - el * 0.12)
        elif river == "Agus":
            swell = (rain / 100.0) * 1.0 * (hrs / 4.0)
            base_depth = max(0.0, swell - el * 0.1)
        elif river == "Coastal":
            coastal_impact = max(0.0, tide * 0.8) + (rain / 150.0)
            base_depth = max(0.0, coastal_impact * (1.0 + hrs * 0.1) - el * 0.15)
        elif river == "None":
            accumulation = (rain / 150.0) * 0.8 * (hrs / 2.0)
            drainage_mitigation = drain / 100.0
            base_depth = max(0.0, accumulation * (1.1 - drainage_mitigation) - el * 0.08)
        else:
            base_depth = 0.0

        time_curve = min(1.0, hrs / 4.5)
        base_depth *= time_curve
        return round(max(0.0, base_depth), 2)

    def run_monte_carlo(self, iterations=100) -> Dict[str, Any]:
        inputs = (self.current_time, self.rainfall, self.tide_level, self.drainage_capacity, self.bridge_failure)
        if hasattr(self, "cached_mc") and self.cached_mc is not None and self.cached_mc_inputs == inputs:
            return self.cached_mc

        barangay_counts = {b["id"]: 0 for b in self.barangays}
        depth_totals = {b["id"]: 0.0 for b in self.barangays}
        road_counts = {r["id"]: 0 for r in self.roads}

        for _ in range(iterations):
            noise_rain = self.rainfall * (0.85 + random.random() * 0.3)
            noise_tide = self.tide_level + (random.random() * 0.6 - 0.3)
            noise_drain = max(0.0, min(100.0, self.drainage_capacity * (0.8 + random.random() * 0.4)))
            temp_bridge_fail = self.bridge_failure or (noise_rain > 220 and random.random() > 0.4)

            iter_override = {
                "rainfall": noise_rain,
                "tideLevel": noise_tide,
                "drainageCapacity": noise_drain,
                "bridgeFailure": temp_bridge_fail,
                "currentTime": self.current_time
            }

            iter_depths = {}
            for b in self.barangays:
                local_noise = (random.random() - 0.5) * 0.2
                depth = round(max(0.0, self.calculate_brgy_depth(b, iter_override) + local_noise), 2)
                iter_depths[b["id"]] = depth
                depth_totals[b["id"]] += depth
                if depth >= 0.3:
                    barangay_counts[b["id"]] += 1

            for r in self.roads:
                from_d = iter_depths[r["from"]]
                to_d = iter_depths[r["to"]]
                avg_depth = (from_d + to_d) / 2.0

                is_blocked = False
                if avg_depth > 0.4:
                    is_blocked = True
                if r["isBridge"] and temp_bridge_fail:
                    if r["from"] in ("B1", "B10") and noise_rain > 150:
                        is_blocked = True
                debris_prob = (noise_rain / 300.0) * 0.08
                if random.random() < debris_prob:
                    is_blocked = True

                if not is_blocked:
                    road_counts[r["id"]] += 1

        brgy_probs = {k: round(v / iterations, 2) for k, v in barangay_counts.items()}
        avg_depths = {k: round(v / iterations, 2) for k, v in depth_totals.items()}
        road_probs = {k: round(v / iterations, 2) for k, v in road_counts.items()}

        feature_importance = [
            {"feature": "Rainfall Intensity", "importance": 75 if self.rainfall > 180 else 55, "correlation": "positive"},
            {"feature": "Mandulog River Level", "importance": 68 if self.rainfall > 120 else 40, "correlation": "positive"},
            {"feature": "Drainage Efficiency", "importance": int(100 - self.drainage_capacity), "correlation": "negative"},
            {"feature": "Ocean Tide Level", "importance": int(self.tide_level * 15 + 15), "correlation": "positive"},
            {"feature": "Bridge Safety", "importance": 85 if self.bridge_failure else 20, "correlation": "negative"}
        ]
        feature_importance.sort(key=lambda x: x["importance"], reverse=True)

        result = {
            "barangayFloodProb": brgy_probs,
            "roadPassabilityProb": road_probs,
            "averageDepths": avg_depths,
            "featureImportance": feature_importance
        }
        self.cached_mc = result
        self.cached_mc_inputs = inputs
        return result

    def find_safe_route(self, start_brgy_id: str, end_center_id: str, mc_results: Dict[str, Any]) -> Dict[str, Any]:
        center = next((c for c in self.centers if c["id"] == end_center_id), None)
        target_brgy_id = center["barangayId"] if center else ""

        if start_brgy_id == target_brgy_id:
            return {
                "routePath": [start_brgy_id],
                "isSafe": True,
                "riskScore": 0,
                "estimatedTimeMin": 0,
                "reasons": ["Already inside target safe evacuation center."]
            }

        distances = {b["id"]: float("inf") for b in self.barangays}
        previous = {b["id"]: None for b in self.barangays}
        queue = [b["id"] for b in self.barangays]
        distances[start_brgy_id] = 0.0

        while len(queue) > 0:
            queue.sort(key=lambda nid: distances[nid])
            u = queue.pop(0)

            if u == target_brgy_id:
                break
            if distances[u] == float("inf"):
                break

            connecting_segments = [
                r for r in self.roads if r["from"] == u or r["to"] == u
            ]

            for road in connecting_segments:
                neighbor = road["to"] if road["from"] == u else road["from"]
                if neighbor not in queue:
                    continue

                prob = mc_results["roadPassabilityProb"].get(road["id"], 1.0)
                road_depth = road["currentDepth"]
                is_failed_bridge = self.bridge_failure and road["isBridge"]

                risk_penalty = 1.0
                if road_depth > 0.4:
                    risk_penalty += (road_depth * 25.0)
                if prob < 0.8:
                    risk_penalty += (1.0 - prob) * 50.0
                if is_failed_bridge:
                    risk_penalty += 10000.0  # Impassable collapsed barrier

                alt_dist = distances[u] + road["distance"] * risk_penalty
                if alt_dist < distances[neighbor]:
                    distances[neighbor] = alt_dist
                    previous[neighbor] = u

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
                "reasons": ["No route available above flooding thresholds. Seek high-ground sheltering!"]
            }

        total_dist = 0.0
        total_fail_rate = 0.0
        bottlenecks = []
        reasons = []

        for j in range(len(path) - 1):
            u_node, v_node = path[j], path[j+1]
            seg = next((r for r in self.roads if (r["from"] == u_node and r["to"] == v_node) or (r["from"] == v_node and r["to"] == u_node)), None)
            if seg:
                total_dist += seg["distance"]
                prob = mc_results["roadPassabilityProb"].get(seg["id"], 1.0)
                total_fail_rate += (1.0 - prob)
                if prob < 0.6:
                    bottlenecks.append(seg["name"])
                    reasons.append(f"Paths cross {seg['name']} possessing a {int((1.0 - prob) * 100)}% risk of severe flooding blockage.")

        base_speed = 4.0
        start_d = next((b["floodDepth"] for b in self.barangays if b["id"] == start_brgy_id), 0.0)
        slowfactor = max(0.1, 1.0 - start_d * 1.5)
        est_time = round((total_dist / (base_speed * slowfactor)) * 60)

        agg_risk = min(100, round((total_fail_rate / max(1, len(path)-1)) * 50 + (start_d * 35)))

        if not reasons:
            reasons.append("Computed optimal dry route leveraging inland bypasses.")

        return {
            "routePath": path,
            "isSafe": agg_risk < 50,
            "riskScore": agg_risk,
            "estimatedTimeMin": est_time,
            "bottlenecks": list(set(bottlenecks)),
            "reasons": list(set(reasons))
        }

    def find_path_between_brgys(self, start_brgy_id: str, end_brgy_id: str, mc_results: Dict[str, Any]) -> List[str]:
        if start_brgy_id == end_brgy_id:
            return [start_brgy_id]

        distances = {b["id"]: float("inf") for b in self.barangays}
        previous = {b["id"]: None for b in self.barangays}
        queue = [b["id"] for b in self.barangays]
        distances[start_brgy_id] = 0.0

        while len(queue) > 0:
            queue.sort(key=lambda nid: distances[nid])
            u = queue.pop(0)

            if u == end_brgy_id:
                break
            if distances[u] == float("inf"):
                break

            connecting_segments = [
                r for r in self.roads if r["from"] == u or r["to"] == u
            ]

            for road in connecting_segments:
                neighbor = road["to"] if road["from"] == u else road["from"]
                if neighbor not in queue:
                    continue

                prob = mc_results["roadPassabilityProb"].get(road["id"], 1.0)
                road_depth = road["currentDepth"]
                is_failed_bridge = self.bridge_failure and road["isBridge"]

                risk_penalty = 1.0
                if road_depth > 0.4:
                    risk_penalty += (road_depth * 25.0)
                if prob < 0.8:
                    risk_penalty += (1.0 - prob) * 50.0
                if is_failed_bridge:
                    risk_penalty += 10000.0

                alt_dist = distances[u] + road["distance"] * risk_penalty
                if alt_dist < distances[neighbor]:
                    distances[neighbor] = alt_dist
                    previous[neighbor] = u

        path = []
        curr = end_brgy_id
        while curr:
            path.insert(0, curr)
            curr = previous[curr]

        if not path or path[0] != start_brgy_id:
            return []
        return path

    def step(self):
        with self.lock:
            if self.current_time >= 6.0:
                self.is_running = False
                return
            
            self.current_time = round(self.current_time + 0.1, 2)
            self.update_hydrology()
            
            mc = self.run_monte_carlo()
            
            # Step Evacuees
            for agent in self.agents:
                if agent["status"] in ("Safe", "Casualty"):
                    continue
                
                # Delayed preparation phase
                if agent["status"] == "Preparing":
                    if self.current_time >= agent["prepTimeHours"]:
                        route = self.find_safe_route(agent["currentBarangayId"], agent["targetCenterId"], mc)
                        if route["routePath"] and len(route["routePath"]) > 1:
                            agent["path"] = route["routePath"]
                            agent["currentPathIndex"] = 0
                            agent["status"] = "Evacuating"
                        else:
                            agent["status"] = "Stuck"
                    
                    # preparation hazard (flash deaths)
                    bg = next((b for b in self.barangays if b["id"] == agent["sourceBarangayId"]), None)
                    if bg and bg["floodDepth"] > 0.5:
                        drowning_chance = 0.08 * (bg["floodDepth"] - 0.5)
                        if random.random() < drowning_chance:
                            agent["status"] = "Casualty"

                # Walking phase
                elif agent["status"] == "Evacuating":
                    curr_idx = agent["currentPathIndex"]
                    src = agent["path"][curr_idx]
                    dst = agent["path"][curr_idx + 1]
                    
                    seg = next((r for r in self.roads if (r["from"] == src and r["to"] == dst) or (r["from"] == dst and r["to"] == src)), None)
                    depth = seg["currentDepth"] if seg else 0.0
                    
                    # Rerouting trigger: if the road is highly flooded (>0.4m), try to dynamically reroute
                    if depth > 0.4:
                        route = self.find_safe_route(src, agent["targetCenterId"], mc)
                        if route["routePath"] and len(route["routePath"]) > 1:
                            agent["path"] = route["routePath"]
                            agent["currentPathIndex"] = 0
                            curr_idx = 0
                            src = agent["path"][0]
                            dst = agent["path"][1]
                            seg = next((r for r in self.roads if (r["from"] == src and r["to"] == dst) or (r["from"] == dst and r["to"] == src)), None)
                            depth = seg["currentDepth"] if seg else 0.0
                        else:
                            agent["status"] = "Stuck"
                            bg = next((b for b in self.barangays if b["id"] == src), None)
                            if bg and bg["floodDepth"] > 0.8:
                                agent["status"] = "RescueNeeded"
                            continue

                    if depth > 0.6:
                        drowning_chance = 0.09 * (depth - 0.6) + 0.02
                        if random.random() < drowning_chance:
                            agent["status"] = "Casualty"
                            continue
                            
                    agent["currentPathIndex"] += 1
                    agent["currentBarangayId"] = dst
                    
                    center = next((c for c in self.centers if c["id"] == agent["targetCenterId"]), None)
                    if dst == center["barangayId"]:
                        agent["status"] = "Safe"
                        center["occupancy"] += 1
                    elif agent["currentPathIndex"] >= len(agent["path"]) - 1:
                        agent["status"] = "Safe"

                # Stranded and RescueNeeded phase
                elif agent["status"] in ("Stuck", "RescueNeeded"):
                    bg = next((b for b in self.barangays if b["id"] == agent["currentBarangayId"]), None)
                    if bg:
                        if bg["floodDepth"] > 0.6:
                            drowning_chance = 0.12 * (bg["floodDepth"] - 0.6)
                            if random.random() < drowning_chance:
                                    agent["status"] = "Casualty"
                            else:
                                if agent["status"] == "Stuck" and bg["floodDepth"] > 0.8:
                                    agent["status"] = "RescueNeeded"
                        elif bg["floodDepth"] > 0.4:
                            if agent["status"] == "Stuck":
                                agent["status"] = "RescueNeeded"

            # Step Rescuers Patrols
            for resc in self.rescuers:
                if resc["status"] == "Idle":
                    target = None
                    for t_a in self.agents:
                        if t_a["status"] in ("RescueNeeded", "Stuck"):
                            if not any(r["targetAgentId"] == t_a["id"] for r in self.rescuers):
                                target = t_a
                                break
                    if target:
                        path = self.find_path_between_brgys(resc["barangayId"], target["currentBarangayId"], mc)
                        if path:
                            resc["status"] = "Dispatched"
                            resc["targetAgentId"] = target["id"]
                            resc["path"] = path
                            resc["currentPathIndex"] = 0
                        else:
                            # Fallback if no routes found (teleport to target for safety dispatch)
                            resc["status"] = "Dispatched"
                            resc["targetAgentId"] = target["id"]
                            resc["barangayId"] = target["currentBarangayId"]
                            resc["path"] = [target["currentBarangayId"]]
                            resc["currentPathIndex"] = 0
                        
                elif resc["status"] == "Dispatched":
                    target = next((a for a in self.agents if a["id"] == resc["targetAgentId"]), None)
                    if not target or target["status"] in ("Safe", "Casualty"):
                        resc["status"] = "Idle"
                        resc["targetAgentId"] = None
                        resc["path"] = []
                        resc["currentPathIndex"] = 0
                        continue
                    
                    # Advance along path to target
                    if resc["currentPathIndex"] < len(resc["path"]) - 1:
                        resc["currentPathIndex"] += 1
                        resc["barangayId"] = resc["path"][resc["currentPathIndex"]]
                    
                    # Arrived at target?
                    if resc["currentPathIndex"] >= len(resc["path"]) - 1:
                        center = next((c for c in self.centers if c["id"] == target["targetCenterId"]), self.centers[0])
                        ret_path = self.find_path_between_brgys(resc["barangayId"], center["barangayId"], mc)
                        resc["status"] = "Returning"
                        resc["targetCenterId"] = center["id"]
                        if ret_path:
                            resc["path"] = ret_path
                            resc["currentPathIndex"] = 0
                        else:
                            resc["path"] = [center["barangayId"]]
                            resc["currentPathIndex"] = 0
                    
                elif resc["status"] == "Returning":
                    target = next((a for a in self.agents if a["id"] == resc["targetAgentId"]), None)
                    center = next((c for c in self.centers if c["id"] == resc["targetCenterId"]), self.centers[0])
                    
                    # Advance along path to center
                    if resc["currentPathIndex"] < len(resc["path"]) - 1:
                        resc["currentPathIndex"] += 1
                        resc["barangayId"] = resc["path"][resc["currentPathIndex"]]
                        
                        # Escorted civilian moves along with the rescuer!
                        if target and target["status"] in ("RescueNeeded", "Stuck", "Evacuating"):
                            target["currentBarangayId"] = resc["barangayId"]
                    
                    # Arrived at evacuation center?
                    if resc["currentPathIndex"] >= len(resc["path"]) - 1:
                        if target:
                            target["status"] = "Safe"
                            target["currentBarangayId"] = center["barangayId"]
                            center["occupancy"] += 1
                            resc["rescuedCount"] += 1
                            
                        resc["status"] = "Idle"
                        resc["targetAgentId"] = None
                        resc["targetCenterId"] = None
                        resc["path"] = []
                        resc["currentPathIndex"] = 0

            self.record_history_step(mc)

    def autoplay_loop(self):
        while True:
            with self.lock:
                running = self.is_running
                curr_t = self.current_time
                
            if running and curr_t < 6.0:
                self.step()
                threading.Event().wait(0.8)  # tick speed 0.8 seconds per step
            else:
                threading.Event().wait(0.5)

# ==========================================
# 3. HTTP REQUEST DISPATCH HANDLER
# ==========================================

engine = SimulationEngine()

# Start background thread for autopilot loop
t_auto = threading.Thread(target=engine.autoplay_loop, daemon=True)
t_auto.start()

class SimulationHTTPHandler(http.server.BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        # Serve Dashboard Root Page
        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(INDEX_HTML.encode("utf-8"))
            return

        # Core API Endpoints
        if path == "/api/state":
            with engine.lock:
                mc = engine.run_monte_carlo()
                
                # Combine dynamic variables
                res_barangays = []
                for b in engine.barangays:
                    res_barangays.append({
                        **b,
                        "floodProb": mc["barangayFloodProb"].get(b["id"], 0.0),
                    })
                    
                res_roads = []
                for r in engine.roads:
                    res_roads.append({
                        **r,
                        "passabilityProb": mc["roadPassabilityProb"].get(r["id"], 1.0),
                    })

                body = {
                    "currentTime": engine.current_time,
                    "rainfall": engine.rainfall,
                    "tideLevel": engine.tide_level,
                    "drainageCapacity": engine.drainage_capacity,
                    "bridgeFailure": engine.bridge_failure,
                    "crowdingFactor": engine.crowding_factor,
                    "initialPopulation": engine.initial_population,
                    "activeScenarioName": engine.scenario_name,
                    "isRunning": engine.is_running,
                    "barangays": res_barangays,
                    "roads": res_roads,
                    "centers": engine.centers,
                    "agents": [
                        {
                            "id": a["id"],
                            "sourceBarangayId": a["sourceBarangayId"],
                            "targetCenterId": a["targetCenterId"],
                            "currentBarangayId": a["currentBarangayId"],
                            "status": a["status"]
                        } for a in engine.agents
                    ],
                    "rescuers": engine.rescuers,
                    "monteCarlo": mc,
                    "history": getattr(engine, "history", [])
                }
                
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(body).encode("utf-8"))
            return



        # Optional download file path helper
        if path == "/simulation.py":
            try:
                with open("/simulation.py", "rb") as f:
                    self.send_response(200)
                    self.send_header("Content-Type", "text/x-python")
                    self.send_header("Content-Disposition", "attachment; filename=\"simulation.py\"")
                    self.end_headers()
                    self.wfile.write(f.read())
                    return
            except Exception:
                self.send_response(404)
                self.end_headers()
                return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # Handle API Mutations
        if path == "/api/reset":
            content_len = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_len).decode('utf-8')
            data = json.loads(post_data) if post_data else {}
            
            scenario = data.get("scenario", "Default")
            engine.reset(scenario)
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "scenario": scenario}).encode("utf-8"))
            return

        if path == "/api/step":
            engine.step()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "currentTime": engine.current_time}).encode("utf-8"))
            return

        if path == "/api/toggle-run":
            with engine.lock:
                engine.is_running = not engine.is_running
                status = "running" if engine.is_running else "paused"
                
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": status}).encode("utf-8"))
            return

        if path == "/api/set-variables":
            content_len = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_len).decode('utf-8')
            data = json.loads(post_data) if post_data else {}
            
            with engine.lock:
                if "rainfall" in data:
                    engine.rainfall = float(data["rainfall"])
                if "tideLevel" in data:
                    engine.tide_level = float(data["tideLevel"])
                if "drainageCapacity" in data:
                    engine.drainage_capacity = float(data["drainageCapacity"])
                if "bridgeFailure" in data:
                    engine.bridge_failure = bool(data["bridgeFailure"])
                if "initialPopulation" in data:
                    new_pop = int(data["initialPopulation"])
                    if new_pop != engine.initial_population:
                        engine.initial_population = new_pop
                        import random
                        flood_prone = ["B1", "B2", "B3", "B7", "B8", "B9", "B10"]
                        engine.agents = []
                        for i in range(engine.initial_population):
                            source = random.choice(flood_prone)
                            target = random.choice(["EC1", "EC2", "EC3", "EC5"])
                            prep_hrs = round(0.5 + random.random() * 1.8, 2)
                            engine.agents.append({
                                "id": f"CIV-{i+1:03d}",
                                "sourceBarangayId": source,
                                "targetCenterId": target,
                                "currentBarangayId": source,
                                "status": "Preparing",
                                "prepTimeHours": prep_hrs,
                                "path": [],
                                "currentPathIndex": 0
                            })
                        for c in engine.centers:
                            c["occupancy"] = 0
                engine.update_hydrology()
                
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))
            return

        if path == "/api/export-csv":
            import csv
            import io

            with engine.lock:
                history_data = list(getattr(engine, "history", []))
                barangays_list = list(engine.barangays)

            # Map barangay IDs to names
            brgy_id_to_name = {b["id"]: b["name"] for b in barangays_list}
            brgy_ids = [b["id"] for b in barangays_list]

            # Generate CSV in memory
            output = io.StringIO()
            writer = csv.writer(output)

            # Build headers
            headers = ["time", "safe", "casualties"] + [f"{brgy_id_to_name.get(bid, bid)}_depth" for bid in brgy_ids]
            writer.writerow(headers)

            for step in history_data:
                row = [
                    step.get("time", 0.0),
                    step.get("safeCount", 0),
                    step.get("casualtyCount", 0)
                ]
                brgy_depths = step.get("barangayDepths", {})
                for bid in brgy_ids:
                    row.append(brgy_depths.get(bid, 0.0))
                writer.writerow(row)

            csv_content = output.getvalue()
            output.close()

            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.send_header("Content-Disposition", 'attachment; filename="simulation_history.csv"')
            self.end_headers()
            self.wfile.write(csv_content.encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

# ==========================================
# 4. GORGEOUS STYLED HTML INTERFACE STRING
# ==========================================

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Iligan City Flood Evacuation Simulation Dashboard</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap');
    
    body {
      font-family: 'Inter', sans-serif;
    }
    .heading-font {
      font-family: 'Space Grotesk', sans-serif;
    }
    .mono-font {
      font-family: 'JetBrains Mono', monospace;
    }
    
    /* Elegant Custom Scrollbars */
    ::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    ::-webkit-scrollbar-track {
      background: #0f172a;
    }
    ::-webkit-scrollbar-thumb {
      background: #334155;
      border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #475569;
    }

    /* Leaflet Premium Dark Styles */
    #leaflet-map {
      background: #070b13;
    }
    .leaflet-container {
      font-family: 'Inter', sans-serif !important;
    }
    .leaflet-bar {
      border: 1px solid rgba(168, 85, 247, 0.2) !important;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
    }
    .leaflet-bar a {
      background-color: #0f172a !important;
      color: #94a3b8 !important;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    .leaflet-bar a:hover {
      background-color: #1e293b !important;
      color: #6366f1 !important;
    }
    .leaflet-control-layers {
      background-color: #0f172a !important;
      color: #f1f5f9 !important;
      border: 1px solid rgba(168, 85, 247, 0.25) !important;
      font-size: 10px !important;
      font-family: 'JetBrains Mono', monospace !important;
      border-radius: 8px !important;
      box-shadow: 0 10px 15px -3px rgba(0,0,0,0.5) !important;
    }
    .leaflet-tooltip {
      background-color: #0d1527 !important;
      color: #f1f5f9 !important;
      border: 1px solid rgba(168, 85, 247, 0.4) !important;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.6) !important;
      font-size: 10px !important;
      font-weight: 600;
      border-radius: 6px !important;
      padding: 6px 10px !important;
    }
    .leaflet-tooltip::before {
      border-top-color: #0d1527 !important;
      border-bottom-color: #0d1527 !important;
    }
  </style>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
</head>
<body class="bg-[#090d16] text-slate-100 min-h-screen overflow-x-hidden flex flex-col selection:bg-purple-600/30 selection:text-white">

  <!-- Header Section -->
  <header class="border-b border-slate-800 bg-[#0f172a] shadow-lg sticky top-0 z-50 px-6 py-4 flex flex-col md:flex-row items-center justify-between gap-4">
    <div class="flex items-center gap-3">
      <h1 class="text-base font-bold tracking-tight uppercase heading-font text-slate-100">
        Iligan City Flood Evacuation Simulation
      </h1>
    </div>
    
    <!-- Top Row Controls / Active Status indicators -->
    <div id="connection-status-panel" class="flex flex-wrap items-center gap-5 font-mono text-[10.5px]">
      <div id="state-rain-tag" class="flex items-center gap-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-sky-400">
        <i data-lucide="cloud-rain" class="h-3.5 w-3.5 animate-bounce"></i>
        <span>RAINFALL: <strong id="val-rainfall">180</strong> mm</span>
      </div>
      <div id="state-tide-tag" class="flex items-center gap-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-emerald-400">
        <i data-lucide="waves" class="h-3.5 w-3.5"></i>
        <span>TIDE: <strong id="val-tide">1.80</strong> m</span>
      </div>
      <div id="state-casualties-tag" class="flex items-center gap-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-slate-400 transition-all duration-300">
        <i id="icon-casualties-top" data-lucide="skull" class="h-3.5 w-3.5 transition-all duration-300"></i>
        <span>FATALITIES: <strong id="val-casualties-top">0</strong> LIVES</span>
      </div>
    </div>
  </header>

  <!-- Main Workspace -->
  <main class="flex-1 max-w-7xl w-full mx-auto p-5 grid grid-cols-1 lg:grid-cols-4 gap-5 items-stretch">
    
    <!-- LEFT SIDEBAR: Sim controls & Variables -->
    <section class="lg:col-span-1 flex flex-col gap-5 justify-start">
      
      <!-- Preset Scenarios -->
      <div class="bg-[#0f172a] border border-slate-800 rounded-2xl p-5 shadow-2xl">
        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-2">
          <i data-lucide="sparkles" class="h-4 w-4 text-purple-400"></i> Disasters Scenarios
        </h3>
        <div class="grid grid-cols-1 gap-2">
          <button onclick="applyScenario('TS Basyang')" class="preset-btn group bg-[#111827] border border-purple-500/20 text-left p-3 rounded-xl hover:border-purple-400/40 hover:bg-purple-950/10 transition-all cursor-pointer">
            <div class="flex justify-between items-center">
              <span class="font-bold text-xs uppercase text-purple-200">TS Basyang</span>
              <span class="text-[9px] bg-purple-500/20 text-purple-300 font-extrabold px-1.5 py-0.5 rounded">Pre-configured</span>
            </div>
            <p class="text-[10px] text-slate-400 mt-1">Simulates tidal swells, swift river flow, & collapsed bridge systems.</p>
          </button>
          
          <button onclick="applyScenario('Super Typhoon')" class="preset-btn text-left p-3 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 transition-all cursor-pointer">
            <span class="font-bold text-xs uppercase text-rose-300 block">Super Typhoon</span>
            <p class="text-[10px] text-slate-400 mt-1">Catastrophic rainfall with zero drainage capacity.</p>
          </button>
          
          <button onclick="applyScenario('High Tide Flash Flood')" class="preset-btn text-left p-3 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 transition-all cursor-pointer">
            <span class="font-bold text-xs uppercase text-amber-300 block">High Tide Flash Flood</span>
            <p class="text-[10px] text-slate-400 mt-1">High ocean tide backing up rivers under heavy rainfall.</p>
          </button>
          
          <button onclick="applyScenario('Default')" class="preset-btn text-left p-3 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 transition-all cursor-pointer">
            <span class="font-bold text-xs uppercase text-[#a855f7] block">Standard Heavy Rain</span>
            <p class="text-[10px] text-slate-400 mt-1">Baseline conditions showing active pathfinding evacuation.</p>
          </button>
        </div>
      </div>
      
      <!-- Interactive Variables Slider -->
      <div id="sliders-panel" class="bg-[#0f172a] border border-slate-800 rounded-2xl p-5 shadow-2xl flex flex-col gap-4">
        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
          <i data-lucide="sliders" class="h-4 w-4 text-purple-400"></i> Physical Controls
        </h3>
        
        <!-- Rainfall -->
        <div class="space-y-1">
          <div class="flex justify-between items-center text-xs font-mono">
            <span class="text-slate-400">Rainfall Amount:</span>
            <span class="text-sky-400 font-bold" id="lbl-rainfall">180 mm</span>
          </div>
          <input type="range" id="input-rainfall" min="50" max="350" step="10" value="180" oninput="changeSliders()" class="w-full h-1.5 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-purple-500">
        </div>
        
        <!-- Tide -->
        <div class="space-y-1">
          <div class="flex justify-between items-center text-xs font-mono">
            <span class="text-slate-400">Sea Tide Level:</span>
            <span class="text-emerald-400 font-bold" id="lbl-tide">1.8 m</span>
          </div>
          <input type="range" id="input-tide" min="0" max="4" step="0.1" value="1.8" oninput="changeSliders()" class="w-full h-1.5 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-purple-500">
        </div>
        
        <!-- Drainage -->
        <div class="space-y-1">
          <div class="flex justify-between items-center text-xs font-mono">
            <span class="text-slate-400">Drainage Efficiency:</span>
            <span class="text-purple-400 font-bold" id="lbl-drainage">65%</span>
          </div>
          <input type="range" id="input-drainage" min="10" max="100" step="5" value="65" oninput="changeSliders()" class="w-full h-1.5 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-purple-500">
        </div>

        <!-- Simulated Citizens Population size -->
        <div class="space-y-1">
          <div class="flex justify-between items-center text-xs font-mono">
            <span class="text-slate-400">Simulated Citizens:</span>
            <span class="text-amber-400 font-bold" id="lbl-population">250 agents</span>
          </div>
          <input type="range" id="input-population" min="50" max="600" step="25" value="250" oninput="changeSliders()" class="w-full h-1.5 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-amber-500 animate-pulse-once">
        </div>

        <!-- Track Specific Agent dropdown -->
        <div class="space-y-1.5 pt-2 border-t border-slate-800/80">
          <div class="flex justify-between items-center text-xs font-mono">
            <span class="text-slate-400">Track Specific Agent:</span>
            <span class="text-purple-400 font-bold" id="lbl-tracked-status">-</span>
          </div>
          <select id="select-active-agent" onchange="trackSelectedAgent()" class="w-full bg-[#090d16] border border-slate-800 rounded-xl px-3 py-2 text-xs font-medium text-slate-200 focus:outline-none focus:border-purple-500 transition-all font-sans cursor-pointer text-ellipsis overflow-hidden">
            <option value="">-- No Agent Selected / Tracked --</option>
          </select>
        </div>
        
        <!-- Bridge failures Toggle -->
        <div class="flex justify-between items-center bg-[#111827] border border-slate-800 p-2.5 rounded-xl mt-1">
          <div class="flex flex-col">
            <span class="text-xs font-bold text-slate-300">Mandulog Bridge Block</span>
            <p class="text-[9px] text-slate-400">Simulate structural failure</p>
          </div>
          <input type="checkbox" id="input-bridge" onchange="changeSliders()" checked class="sr-only peer">
          <label for="input-bridge" class="relative w-9 h-5 bg-slate-850 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-slate-300 after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-purple-600 cursor-pointer"></label>
        </div>
      </div>
      
      <!-- Simulation Stepping buttons -->
      <div class="bg-[#0f172a] border border-slate-800 rounded-2xl p-5 shadow-2xl">
        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-2">
          <i data-lucide="play" class="h-4 w-4 text-purple-400"></i> Dispatch Controls
        </h3>
        <div class="flex flex-col gap-2 font-mono">
          <button id="btn-toggle-play" onclick="togglePlay()" class="w-full py-2.5 rounded-xl border border-emerald-500/30 text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/20 font-bold tracking-tight flex items-center justify-center gap-2 transition-all cursor-pointer text-xs">
            <i data-lucide="play" class="h-4 w-4"></i> START SIMULATOR AUTOMATION
          </button>
          <div class="grid grid-cols-2 gap-2">
            <button onclick="stepSim()" class="py-2 bg-slate-800/80 hover:bg-slate-800 border border-slate-700/50 rounded-xl font-bold flex items-center justify-center gap-1 transition-all text-[11px] cursor-pointer text-slate-200">
              <i data-lucide="skip-forward" class="h-3.5 w-3.5"></i> TICK 0.1 hr
            </button>
            <button onclick="resetSim()" class="py-2 bg-slate-800/80 hover:bg-slate-800 border border-slate-700/50 rounded-xl font-bold flex items-center justify-center gap-1 transition-all text-[11px] cursor-pointer text-slate-200">
              <i data-lucide="rotate-ccw" class="h-3.5 w-3.5"></i> HARD RESET
            </button>
          </div>
          <div class="grid grid-cols-2 gap-2 mt-1">
            <button id="btn-export-csv" onclick="exportCSV()" class="py-2 rounded-xl border border-sky-500/30 text-sky-400 bg-sky-500/10 hover:bg-sky-500/20 font-bold tracking-tight flex items-center justify-center gap-1.5 transition-all cursor-pointer text-[10.5px]">
              <i data-lucide="download" class="h-3.5 w-3.5"></i> EXPORT CSV
            </button>
            <button id="btn-export-academic" onclick="openAcademicModal()" class="py-2 rounded-xl border border-purple-500/30 text-purple-400 bg-purple-500/10 hover:bg-purple-500/20 font-bold tracking-tight flex items-center justify-center gap-1.5 transition-all cursor-pointer text-[10.5px]">
              <i data-lucide="image" class="h-3.5 w-3.5 animate-pulse"></i> EXPORT PHOTOS
            </button>
          </div>
        </div>
      </div>
      
    </section>

    <!-- RIGHT/MAIN AREA: Map & Statistics (col span 3) -->
    <section class="lg:col-span-3 flex flex-col gap-5">
      
      <!-- Top Hour Telemetry and Safe Count status -->
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        
        <!-- Time card -->
        <div class="bg-[#0f172a] border border-slate-800 p-4 rounded-xl flex items-center gap-3">
          <div class="p-2.5 bg-purple-500/10 border border-purple-500/20 rounded-xl shrink-0">
            <i data-lucide="clock" class="text-purple-400 h-5 w-5"></i>
          </div>
          <div>
            <span class="text-[9px] uppercase font-bold text-slate-500 block">Incident Clock</span>
            <strong class="text-lg font-mono text-purple-100 block" id="lbl-clock">H-0.0 Hours</strong>
            <span class="text-[8.5px] text-slate-400 block" id="lbl-time-status">Delaying departure...</span>
          </div>
        </div>
        
        <!-- Protected Citizens card -->
        <div class="bg-[#0f172a] border border-slate-800 p-4 rounded-xl flex items-center gap-3">
          <div class="p-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-xl shrink-0">
            <i data-lucide="shield" class="text-emerald-400 h-5 w-5 animate-pulse"></i>
          </div>
          <div class="min-w-0 flex-1">
            <span class="text-[9px] uppercase font-bold text-slate-500 block">Protected Citizens</span>
            <strong class="text-base text-emerald-400 block truncate" id="lbl-safescore">0 Saved</strong>
            <span class="text-[8.5px] text-slate-500 block">Successful evacuations</span>
          </div>
        </div>

        <!-- Fatalities card -->
        <div id="card-casualties" class="bg-[#0f172a] border border-slate-800 p-4 rounded-xl flex items-center gap-3 transition-all duration-300">
          <div id="icon-casualties-wrapper" class="p-2.5 bg-slate-500/10 border border-slate-500/20 rounded-xl shrink-0 transition-all duration-300">
            <i id="icon-casualties" data-lucide="skull" class="text-slate-400 h-5 w-5 transition-all duration-300"></i>
          </div>
          <div class="min-w-0 flex-1">
            <span class="text-[9px] uppercase font-bold text-slate-500 block">Fatalities / Deaths</span>
            <strong class="text-base text-slate-400 block truncate" id="lbl-casualties">0 Lost</strong>
            <span class="text-[8.5px] text-slate-500 block">Simulated drowning cases</span>
          </div>
        </div>

        <!-- Shelter space -->
        <div class="bg-[#0f172a] border border-slate-800 p-4 rounded-xl flex items-center gap-3">
          <div class="p-2.5 bg-sky-500/10 border border-sky-500/20 rounded-xl shrink-0">
            <i data-lucide="home" class="text-sky-400 h-5 w-5"></i>
          </div>
          <div class="min-w-0 flex-1">
            <span class="text-[9px] uppercase font-bold text-slate-500 block">Active Evacuation Occupancy</span>
            <strong class="text-base text-sky-450 block truncate" id="lbl-occupancy">0 / 7,300 Citizens (0%)</strong>
            <span class="text-[8.5px] text-slate-500 block">MSU-IIT, Del Carmen & Tubod gyms combined</span>
          </div>
        </div>

        <!-- Active dispatches -->
        <div class="bg-[#0f172a] border border-slate-800 p-4 rounded-xl flex items-center gap-3">
          <div class="p-2.5 bg-amber-500/10 border border-amber-500/20 rounded-xl shrink-0">
            <i data-lucide="truck" class="text-amber-400 h-5 w-5"></i>
          </div>
          <div class="min-w-0 flex-1">
            <span class="text-[9px] uppercase font-bold text-slate-500 block">Specialist Rescue patrols</span>
            <strong class="text-base text-amber-400 block truncate" id="lbl-rescue-status">0 En Route Tasks</strong>
            <span class="text-[8.5px] text-slate-500 block" id="lbl-total-rescues">Total saved: 0 citizens</span>
          </div>
        </div>

      </div>

      <!-- MIDDLE LAYER: INTERACTIVE MAP & INSPECTOR GRID -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
        
        <!-- Live Map Box (2 cols) -->
        <div class="md:col-span-2 bg-[#0f172a] border border-slate-800 rounded-2xl overflow-hidden shadow-2xl relative flex flex-col items-center justify-between p-4 min-h-[520px]">
          <div class="w-full flex items-center justify-between border-b border-slate-900 pb-3 mb-2 shrink-0">
            <div class="flex items-center gap-2">
              <span class="w-2 h-2 rounded-full bg-emerald-500 animate-ping shrink-0" style="animation-duration: 2s;"></span>
              <h3 class="text-xs font-bold text-slate-200 uppercase tracking-widest leading-none heading-font">
                Satellite Evacuation Tracking Platform
              </h3>
            </div>
            <span class="text-[9px] text-slate-450 block leading-none font-mono">INTEGRATED GIS LEVEL 13 FEED</span>
          </div>
          
          <!-- Loading overlay -->
          <div id="map-loader" class="absolute inset-0 bg-[#090d16]/80 flex flex-col justify-center items-center z-20 pointer-events-none transition-opacity opacity-0">
            <div class="w-8 h-8 rounded-full border-2 border-purple-500 border-t-transparent animate-spin"></div>
            <span class="text-xs text-slate-400 mt-2">Computing Monte Carlo Flows...</span>
          </div>

          <!-- Leaflet Photo Map Container -->
          <div id="leaflet-map-container" class="flex-grow w-full h-[440px] min-h-[440px] pointer-events-auto rounded-xl border border-slate-900/65 relative z-10 overflow-hidden bg-[#070b13]">
            <div id="leaflet-map" class="w-full h-full"></div>
          </div>

          <!-- Map Legend footer -->
          <div class="w-full flex flex-wrap justify-between items-center text-[9px] font-mono border-t border-slate-900 pt-3 mt-3 text-slate-400 gap-2">
            <div class="flex flex-wrap items-center gap-x-4 gap-y-1">
              <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-[#10b981] block"></span> Sheltered</span>
              <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-[#eab308] block"></span> Evacuating</span>
              <span class="flex items-center gap-1.5"><span class="w-2 i h-2 rounded-full bg-[#ef4444] block animate-pulse"></span> Stuck / Rescue Required</span>
              <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-[#1e293b] border-2 border-[#ffedd5] block"></span> SAR Responder</span>
            </div>
            <div class="flex items-center gap-3">
              <span class="flex items-center gap-1"><span class="w-2.5 h-1 bg-[#0ea5e9] block"></span> Dry road</span>
              <span class="flex items-center gap-1"><span class="w-2.5 h-1 bg-[#ef4444] block"></span> Flooded</span>
            </div>
          </div>
        </div>

        <!-- Telemetry Node Inspector Sheet (1 col) -->
        <div class="bg-[#0f172a] border border-slate-800 rounded-2xl p-5 shadow-2xl flex flex-col gap-4 select-none">
          <div class="border-b border-slate-900 pb-2">
            <span class="text-[9px] font-bold text-purple-400 uppercase tracking-widest block">Core Telemetry</span>
            <h4 class="text-sm font-bold text-slate-200 uppercase tracking-widest heading-font" id="inspect-title">Poblacion District</h4>
          </div>
          
          <!-- Dynamic details content -->
          <div class="flex-grow flex flex-col justify-between" id="inspect-panel">
            <div class="space-y-3.5 text-xs">
              
              <!-- Segment details -->
              <div class="grid grid-cols-2 gap-3 pb-3 border-b border-slate-900">
                <div>
                  <span class="text-[10px] text-slate-500 block">Average Elevation</span>
                  <strong class="text-slate-300 font-mono" id="inspect-elevation">4 meters</strong>
                </div>
                <div>
                  <span class="text-[10px] text-slate-500 block">Population</span>
                  <strong class="text-slate-300 font-mono" id="inspect-population">8,900 pop</strong>
                </div>
              </div>
              
              <div class="space-y-1">
                <span class="text-[10px] text-slate-500 block">Water Source Proximity Risk</span>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-[#38bdf8]/15 text-[#38bdf8] uppercase" id="inspect-proximity">Coastal Basin</span>
              </div>

              <!-- Live Hydrology telemetry status -->
              <div class="space-y-1.5 p-3.5 bg-slate-950 border border-slate-900 rounded-xl">
                <span class="text-[10px] text-slate-500 uppercase tracking-wider block">Live Hydrological depth</span>
                <div class="flex items-baseline gap-1">
                  <span class="text-xl font-bold font-mono text-purple-300" id="inspect-depth">1.21 meters</span>
                  <span class="text-[10px] text-slate-500 font-mono" id="inspect-risk-label">High Flood Zone</span>
                </div>
                
                <!-- Monte Carlo probabilities -->
                <div class="mt-2.5 pt-2 border-t border-slate-900/40">
                  <span class="text-[10px] text-slate-500 block">Monte Carlo Runoff Probability:</span>
                  <div class="flex items-center gap-2 mt-1">
                    <div class="flex-1 bg-slate-900 h-2 rounded-full overflow-hidden">
                      <div class="h-full bg-gradient-to-r from-purple-500 to-indigo-500" style="width: 82%" id="inspect-prob-bar"></div>
                    </div>
                    <span class="text-[10px] font-mono font-bold text-slate-300" id="inspect-prob-txt">82% Chance</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="bg-purple-950/5 border border-purple-950/20 p-3 rounded-xl flex items-start gap-2.5 mt-4">
              <i data-lucide="info" class="text-purple-400 shrink-0 h-4 w-4 mt-0.5"></i>
              <div>
                <span class="text-[10px] font-black uppercase text-purple-300 mb-0.5 block">Explorable Node Inspect</span>
                <p class="text-[10px] text-slate-400 leading-normal">Hydrological equations calculate levels recursively across all Iligan water channels.</p>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- RESEARCH ANALYTICS PANEL: DISASTER VIABILITY & SITUATIONAL AWARENESS (PVA EQUIVALENTS) -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">
        
        <!-- Figure 1: Overall Comparative Hazard Risk -->
        <div class="bg-[#0f172a] border border-slate-800 rounded-2xl p-5 shadow-2xl flex flex-col h-[400px]">
          <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3 flex items-center justify-between font-mono">
            <span><strong class="text-purple-400">Figure 1:</strong> Comparative Flood Hazard Risk (Monte Carlo)</span>
            <span class="text-[9px] bg-purple-950/40 text-purple-300 border border-purple-800/30 px-1.5 py-0.5 rounded font-bold">LIVE STATS</span>
          </h3>
          <p class="text-[10px] text-slate-500 mb-4 leading-normal">Horizontal comparative risk assessment showing the proportion of simulated runs where the water levels exceed critical safety baselines for each Iligan Barangay.</p>
          <div class="flex-1 overflow-y-auto space-y-2.5 pr-1" id="fig1-bar-container">
            <!-- Dynamically populated rows for B1 to B12 -->
          </div>
        </div>

        <!-- Figure 2: Trajectories over Time -->
        <div class="bg-[#0f172a] border border-slate-800 rounded-2xl p-5 shadow-2xl flex flex-col h-[400px]">
          <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3 flex items-center justify-between font-mono">
            <span><strong class="text-purple-400">Figure 2:</strong> Evacuation & Casualty Risk Trajectories</span>
            <span class="text-[9px] bg-purple-950/40 text-purple-300 border border-purple-800/30 px-1.5 py-0.5 rounded font-bold">HOUR 0 - 6</span>
          </h3>
          <p class="text-[10px] text-slate-500 mb-3 leading-normal">Time-series trajectories representing the dynamic reallocation of status types among the simulated agent cohort over the 6-hour time step.</p>
          
          <!-- Key Legend -->
          <div class="flex flex-wrap gap-x-4 gap-y-1 mb-2.5 text-[9px] font-mono border-b border-slate-900 pb-2">
            <span class="flex items-center gap-1.5 text-emerald-400"><span class="w-2.5 h-1.5 bg-emerald-500 rounded-sm"></span> Safe (Scaled)</span>
            <span class="flex items-center gap-1.5 text-rose-500"><span class="w-2.5 h-1.5 bg-rose-500 rounded-sm"></span> Casualties</span>
            <span class="flex items-center gap-1.5 text-yellow-400"><span class="w-2.5 h-1.5 bg-yellow-500 rounded-sm"></span> Evacuating</span>
            <span class="flex items-center gap-1.5 text-purple-400"><span class="w-2.5 h-1.5 bg-purple-500 rounded-sm"></span> Preparing</span>
            <span class="flex items-center gap-1.5 text-orange-400"><span class="w-2.5 h-1.5 bg-orange-500 rounded-sm"></span> Stuck/Needs Rescue</span>
          </div>

          <div class="flex-1 relative" id="fig2-svg-container">
            <!-- Draw beautiful vanilla SVG lines -->
            <svg id="fig2-svg" class="w-full h-full text-slate-400 font-mono text-[9px]" viewBox="0 0 450 200" preserveAspectRatio="none">
              <!-- Axes and Labels populated by JS -->
            </svg>
          </div>
        </div>

        <!-- Figure 3: Spatial-Temporal Risk Heatmap -->
        <div class="bg-[#0f172a] border border-slate-800 rounded-2xl p-5 shadow-2xl flex flex-col h-[450px]">
          <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3 flex items-center justify-between font-mono">
            <span><strong class="text-purple-400">Figure 3:</strong> Spatial-Temporal Flood Risk Heatmap Matrix</span>
            <span class="text-[9px] bg-purple-950/40 text-purple-300 border border-purple-800/30 px-1.5 py-0.5 rounded font-bold">Hour vs Location</span>
          </h3>
          <p class="text-[10px] text-slate-500 mb-3 leading-normal">Double-variable analytical grid showcasing the escalation of flood blockage probability across space (Y-axis: Barangays) and time (X-axis: H-0.0 to H-6.0).</p>
          <div class="flex-1 overflow-x-auto overflow-y-auto">
            <div class="min-w-[450px] h-full flex flex-col" id="fig3-heatmap-table">
              <!-- Grid generated in JS -->
            </div>
          </div>
          <div class="flex justify-end items-center gap-3 text-[9px] text-slate-500 mt-2 font-mono">
            <span>0% Safe</span>
            <div class="w-24 h-1.5 rounded-full bg-gradient-to-r from-[#0d121e] via-amber-600 to-rose-600"></div>
            <span>100% Blocked / Deep</span>
          </div>
        </div>

        <!-- Figure 4: 4-Panel Location-Specific Viability -->
        <div class="bg-[#0f172a] border border-slate-800 rounded-2xl p-5 shadow-2xl flex flex-col h-[450px]">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest font-mono">
              <strong class="text-purple-400">Figure 4:</strong> 4-Panel Site Viability detail monitor
            </h3>
            
            <div class="flex items-center gap-2">
              <label class="text-[9px] font-bold text-slate-500 uppercase font-mono">inspect site:</label>
              <select id="select-research-barangay" onchange="updateResearchDashboard()" class="bg-[#090d16] border border-slate-800 rounded-lg px-2 py-1 text-[10px] font-medium text-slate-200 focus:outline-none focus:border-purple-500 cursor-pointer">
                <!-- Populated programmatically -->
              </select>
            </div>
          </div>
          
          <p class="text-[10px] text-slate-500 mb-3 leading-normal">Comprehensive deep-dive analysis of survival and hazard variables for the selected local site showing Monte Carlo trajectories, local outcomes, drowning hazards, and environmental factors.</p>
          
          <!-- 2x2 Bento Subgrid -->
          <div class="grid grid-cols-2 gap-3 flex-1">
            <!-- 4A: Depth Trajectory Envelope -->
            <div class="bg-slate-950/50 border border-slate-900 rounded-xl p-2.5 flex flex-col justify-between h-[150px]">
              <span class="text-[9px] font-bold text-slate-500 uppercase tracking-wider block font-mono">4A. Simulated Depth Trajectory (+/- 2 S.D. Confidence Envelope)</span>
              <div class="flex-1 relative mt-1">
                <svg id="fig4a-svg" class="w-full h-full text-slate-500 font-mono text-[8px]" viewBox="0 0 200 100" preserveAspectRatio="none">
                  <!-- JS generated -->
                </svg>
              </div>
            </div>

            <!-- 4B: Outcome Distribution -->
            <div class="bg-slate-950/50 border border-slate-900 rounded-xl p-2.5 flex flex-col justify-between h-[150px]">
              <span class="text-[9px] font-bold text-slate-500 uppercase tracking-wider block font-mono">4B. Population Outcome Histogram</span>
              <div class="flex-1 relative mt-1">
                <svg id="fig4b-svg" class="w-full h-full text-slate-500 font-mono text-[8px]" viewBox="0 0 200 100" preserveAspectRatio="none">
                  <!-- JS generated -->
                </svg>
              </div>
            </div>

            <!-- 4C: Casualty Hazard Profile -->
            <div class="bg-slate-950/50 border border-slate-900 rounded-xl p-2.5 flex flex-col justify-between h-[130px]">
              <span class="text-[9px] font-bold text-slate-500 uppercase tracking-wider block font-mono">4C. Drowning Casualty Hazard Curve</span>
              <div class="flex-1 relative mt-1">
                <svg id="fig4c-svg" class="w-full h-full text-slate-500 font-mono text-[8px]" viewBox="0 0 200 80" preserveAspectRatio="none">
                  <!-- JS generated -->
                </svg>
              </div>
            </div>

            <!-- 4D: Env Parameters -->
            <div class="bg-slate-950/50 border border-slate-900 rounded-xl p-2.5 flex flex-col justify-between h-[130px]">
              <span class="text-[9px] font-bold text-slate-500 uppercase tracking-wider block font-mono">4D. Site Vulnerability Attributes</span>
              <div class="flex-1 grid grid-cols-2 gap-2 text-[9px] leading-tight font-sans mt-2" id="fig4d-stats">
                <!-- JS generated -->
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- BOTTOM CARS LIST: FLEET STATUS LOGS -->
      <div class="bg-[#0f172a] border border-indigo-950/40 rounded-xl p-5 shadow-lg flex flex-col">
        <h4 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2 font-mono">
          <i data-lucide="shield" class="h-4.5 w-4.5 text-purple-400 shrink-0"></i> CDRRMC search and rescue (sar) fleet status logs
        </h4>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3" id="rescue-fleet-panel">
          <!-- Dynamically populated rescuers cards -->
        </div>
      </div>

    </section>

  </main>

  <!-- Footer -->
  <footer class="border-t border-slate-800 bg-[#0b0e14] py-4 text-center text-[10.5px] text-slate-500">
    <div class="max-w-7xl mx-auto px-5 flex flex-col md:flex-row items-center justify-between gap-2.5">
      <span>© 2026 Mindanawa Disaster Informatics Lab (MDIL). All rights reserved.</span>
      <div class="flex items-center gap-4">
        <span>Inspired by tropical Storm Basyang disasters</span>
      </div>
    </div>
  </footer>

  <!-- ACADEMIC RESEARCH REPORT & FIGURE GENERATOR MODAL -->
  <div id="academic-modal-overlay" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 hidden" style="z-index: 99999;">
    <div class="bg-slate-900 border border-slate-850 rounded-2xl w-full max-w-6xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden">
      
      <!-- Modal Header -->
      <div class="bg-[#0b0f19] border-b border-slate-800 px-6 py-4 flex items-center justify-between">
        <div>
          <h2 class="text-sm font-extrabold uppercase tracking-widest text-slate-100 flex items-center gap-2 font-mono">
            <i data-lucide="image" class="text-purple-400 h-5 w-5"></i> Academic Figures Exporter & Draft Report
          </h2>
          <p class="text-[10.5px] text-slate-400 mt-0.5">Generate, custom-configure, and download high-resolution research-ready photos for scientific publication.</p>
        </div>
        <button onclick="closeAcademicModal()" class="text-slate-400 hover:text-slate-100 p-1.5 rounded-lg hover:bg-slate-800 transition-colors cursor-pointer">
          <i data-lucide="x" class="h-5 w-5"></i>
        </button>
      </div>

      <!-- Modal Toolbar -->
      <div class="bg-slate-950/50 border-b border-slate-800 px-6 py-3 flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <label class="text-xs font-mono text-slate-400 font-bold">Figure 4 Target Location:</label>
          <select id="academic-barangay-select" onchange="renderAcademicFigures()" class="bg-[#090d16] border border-slate-700/80 rounded-lg px-2.5 py-1 text-xs text-slate-250 focus:outline-none focus:border-purple-500 cursor-pointer text-slate-200">
            <!-- Populated via javascript -->
          </select>
        </div>
        
        <div class="flex items-center gap-2">
          <button onclick="window.print()" class="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-bold font-sans flex items-center gap-1.5 cursor-pointer transition-all">
            <i data-lucide="printer" class="h-3.5 w-3.5"></i> PRINT MANUSCRIPT (PDF)
          </button>
          <button onclick="downloadAllFiguresBundle()" class="px-3.5 py-1.5 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-xs font-bold font-sans flex items-center gap-1.5 cursor-pointer transition-all">
            <i data-lucide="download-cloud" class="h-3.5 w-3.5 animate-bounce"></i> DOWNLOAD ALL FIGURES
          </button>
        </div>
      </div>

      <!-- Scrollable Manuscript Area -->
      <div class="flex-1 overflow-y-auto bg-slate-950 p-6 flex justify-center">
        <!-- Paper Container -->
        <div id="manuscript-paper" class="w-full max-w-[850px] bg-white text-slate-900 px-10 py-12 shadow-2xl font-serif leading-relaxed text-justify relative select-text mb-6 rounded-lg">
          
          <!-- Figures Catalog Heading -->
          <div class="border-b border-double border-slate-300 pb-4 mb-8 text-center">
            <h1 class="text-xl font-extrabold uppercase tracking-tight text-slate-950 leading-tight" style="font-family: Georgia, serif;">
              Academic Figures & Scientific Plates Catalog
            </h1>
            <p class="text-[11px] font-sans text-slate-500 mt-1 italic">
              High-Resolution Resolution Verified Evacuation Simulation Outputs for Scientific Publication
            </p>
          </div>

          <!-- FIGURE 1 PLATE -->
          <div class="my-6 bg-slate-50 border border-slate-250 p-4 rounded-xl flex flex-col items-center">
            <div class="w-full flex justify-between items-center mb-2 font-sans border-b border-slate-200 pb-1.5">
              <span class="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Figure 1 Plate (Scientific Bar Chart)</span>
              <button onclick="exportSingleFigure('academic-fig1-svg', 'Figure1_Comparative_Hazard_Risk.png')" class="px-2 py-1 bg-white hover:bg-purple-55 text-purple-650 font-bold border border-purple-200 hover:border-purple-300 rounded text-[9.5px] flex items-center gap-1 cursor-pointer transition-all shadow-sm">
                <i data-lucide="download-cloud" class="h-3 w-3"></i> Download Photo
              </button>
            </div>
            <!-- Canvas container for SVG -->
            <svg id="academic-fig1-svg" viewBox="0 0 600 320" class="w-full bg-white max-w-[550px] border border-slate-100 rounded"></svg>
            <p class="mt-3 text-[10px] text-slate-600 italic font-sans leading-relaxed text-center w-full max-w-[520px]">
              <strong class="font-bold text-slate-800 not-italic">Figure 1:</strong> Comparative baseline flood risk percentage across simulated Iligan City Barangays. Values model water infiltration rates relative to localized topological elevations and drainage capabilities.
            </p>
          </div>

          <!-- FIGURE 2 PLATE -->
          <div class="my-6 bg-slate-50 border border-slate-250 p-4 rounded-xl flex flex-col items-center">
            <div class="w-full flex justify-between items-center mb-2 font-sans border-b border-slate-200 pb-1.5">
              <span class="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Figure 2 Plate (Time-Series Line Chart)</span>
              <button onclick="exportSingleFigure('academic-fig2-svg', 'Figure2_State_Trajectories.png')" class="px-2 py-1 bg-white hover:bg-purple-55 text-purple-650 font-bold border border-purple-200 hover:border-purple-300 rounded text-[9.5px] flex items-center gap-1 cursor-pointer transition-all shadow-sm">
                <i data-lucide="download-cloud" class="h-3 w-3"></i> Download Photo
              </button>
            </div>
            <svg id="academic-fig2-svg" viewBox="0 0 600 320" class="w-full bg-white max-w-[550px] border border-slate-100 rounded"></svg>
            <p class="mt-3 text-[10px] text-slate-600 italic font-sans leading-relaxed text-center w-full max-w-[520px]">
              <strong class="font-bold text-slate-800 not-italic">Figure 2:</strong> Absolute citizen state trajectories (Safe, Casuality, Evacuating, Preparing, and Stuck) over the continuous 0.0 to 6.0 hours simulation horizon.
            </p>
          </div>

          <!-- FIGURE 3 PLATE -->
          <div class="my-6 bg-slate-50 border border-slate-250 p-4 rounded-xl flex flex-col items-center">
            <div class="w-full flex justify-between items-center mb-2 font-sans border-b border-slate-200 pb-1.5">
              <span class="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Figure 3 Plate (Danger Matrix Heatmap)</span>
              <button onclick="exportSingleFigure('academic-fig3-svg', 'Figure3_SpatialTemporal_Heatmap.png')" class="px-2 py-1 bg-white hover:bg-purple-55 text-purple-650 font-bold border border-purple-200 hover:border-purple-300 rounded text-[9.5px] flex items-center gap-1 cursor-pointer transition-all shadow-sm">
                <i data-lucide="download-cloud" class="h-3 w-3"></i> Download Photo
              </button>
            </div>
            <svg id="academic-fig3-svg" viewBox="0 0 700 350" class="w-full bg-white max-w-[580px] border border-slate-100 rounded"></svg>
            <p class="mt-3 text-[10px] text-slate-600 italic font-sans leading-relaxed text-center w-full max-w-[520px]">
              <strong class="font-bold text-slate-800 not-italic">Figure 3:</strong> Matrix of spatial-temporal hazard intensities compiled across hourly step divisions. The color scale grades local danger profiles from negligible risk (0.0) up to fatal flood hazard conditions (1.0).
            </p>
          </div>

          <!-- FIGURE 4 PLATE (COMPOSITE) -->
          <div class="my-6 bg-slate-50 border border-slate-250 p-4 rounded-xl flex flex-col items-center">
            <div class="w-full flex justify-between items-center mb-2 font-sans border-b border-slate-200 pb-1.5">
              <span class="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Figure 4 Plate (4-Panel Localized Comp)</span>
              <button onclick="exportSingleFigure('academic-fig4-svg', 'Figure4_Localized_4Panel.png')" class="px-2 py-1 bg-white hover:bg-purple-55 text-purple-650 font-bold border border-purple-200 hover:border-purple-300 rounded text-[9.5px] flex items-center gap-1 cursor-pointer transition-all shadow-sm">
                <i data-lucide="download-cloud" class="h-3 w-3"></i> Download Photo
              </button>
            </div>
            <svg id="academic-fig4-svg" viewBox="0 0 800 520" class="w-full bg-white max-w-[580px] border border-slate-100 rounded"></svg>
            <p class="mt-3 text-[10px] text-slate-600 italic font-sans leading-relaxed text-center w-full max-w-[520px]">
              <strong class="font-bold text-slate-800 not-italic">Figure 4:</strong> 4-panel analysis sheet showing localized hydrological dynamics for selected Barangay. Panel (A) models local water levels over time, Panel (B) states local outcome percentages, Panel (C) charts depth-vulnerability metrics, and Panel (D) lists geomorphological parameters.
            </p>
          </div>

        </div>
      </div>
    </div>
  </div>

  <!-- CORE CODE LOGIC -->
  <script>
    let simState = null;
    let selectedNodeId = "B3"; // start by inspecting Poblacion
    let selectedRouteSource = "B1";
    let selectedRouteTarget = "EC1";
    let trackedAgentId = ""; // Track specific active citizen
    
    // Leaflet map elements
    let leafletMap = null;
    let leafletRoadsGroup = null;
    let leafletMarkersGroup = null;
    let leafletAgentsGroup = null;
    let leafletRescuersGroup = null;

    // Smooth agent animation positioning cache (60 FPS interpolation tracker)
    let clientAgentPositions = {}; // id -> { currentLat, currentLng, targetLat, targetLng }
    let clientRescuerPositions = {}; // id -> { currentLat, currentLng, targetLat, targetLng }
    let leafletAgentMarkers = {}; // id -> L.circleMarker
    let leafletRescuerMarkers = {}; // id -> L.marker
    let animationLoopStarted = false;

    function startAgentAnimationLoop() {
      if (animationLoopStarted) return;
      animationLoopStarted = true;

      function tick() {
        // Intercept and smoothly slide civilian agents
        for (const id in clientAgentPositions) {
          const pos = clientAgentPositions[id];
          const marker = leafletAgentMarkers[id];
          if (!marker) continue;

          const dLat = pos.targetLat - pos.currentLat;
          const dLng = pos.targetLng - pos.currentLng;

          if (Math.abs(dLat) < 0.00001 && Math.abs(dLng) < 0.00001) {
            pos.currentLat = pos.targetLat;
            pos.currentLng = pos.targetLng;
          } else {
            pos.currentLat += dLat * 0.045; // buttery smooth continuous easing factor
            pos.currentLng += dLng * 0.045;
          }
          marker.setLatLng([pos.currentLat, pos.currentLng]);
        }

        // Intercept and smoothly slide rescuers
        for (const id in clientRescuerPositions) {
          const pos = clientRescuerPositions[id];
          const marker = leafletRescuerMarkers[id];
          if (!marker) continue;

          const dLat = pos.targetLat - pos.currentLat;
          const dLng = pos.targetLng - pos.currentLng;

          if (Math.abs(dLat) < 0.00001 && Math.abs(dLng) < 0.00001) {
            pos.currentLat = pos.targetLat;
            pos.currentLng = pos.targetLng;
          } else {
            pos.currentLat += dLat * 0.045; // matched continuous easing factor
            pos.currentLng += dLng * 0.045;
          }
          marker.setLatLng([pos.currentLat, pos.currentLng]);
        }

        requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    }

    function clearAgentMarkers() {
      clientAgentPositions = {};
      clientRescuerPositions = {};
      if (leafletAgentsGroup) leafletAgentsGroup.clearLayers();
      if (leafletRescuersGroup) leafletRescuersGroup.clearLayers();
      leafletAgentMarkers = {};
      leafletRescuerMarkers = {};
    }

    function initLeafletMap() {
      if (leafletMap) {
        setTimeout(() => { leafletMap.invalidateSize(); }, 150);
        return;
      }
      
      // Center near Barangay Pala-o / Poblacion: Lat 8.225, Lng 124.248
      leafletMap = L.map('leaflet-map', {
        zoomControl: false,
        attributionControl: false
      }).setView([8.225, 124.248], 13);
      
      L.control.zoom({ position: 'bottomright' }).addTo(leafletMap);
      
      const esriSatellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 18
      });
      
      const darkMatter = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 20
      });
      
      esriSatellite.addTo(leafletMap);
      
      const baseMaps = {
        "Satellite Image": esriSatellite,
        "Dark Vector Streets": darkMatter
      };
      
      L.control.layers(baseMaps, null, { collapsed: true, position: 'topright' }).addTo(leafletMap);
      
      leafletRoadsGroup = L.layerGroup().addTo(leafletMap);
      leafletMarkersGroup = L.layerGroup().addTo(leafletMap);
      leafletAgentsGroup = L.layerGroup().addTo(leafletMap);
      leafletRescuersGroup = L.layerGroup().addTo(leafletMap);
      
      startAgentAnimationLoop();
      
      setTimeout(() => { leafletMap.invalidateSize(); }, 250);
    }

    async function fetchState() {
      try {
        const res = await fetch("/api/state");
        const data = await res.json();
        simState = data;
        
        // Update stats
        document.getElementById("val-rainfall").innerText = parseInt(data.rainfall);
        document.getElementById("val-tide").innerText = parseFloat(data.tideLevel).toFixed(2);
        
        document.getElementById("lbl-rainfall").innerText = parseInt(data.rainfall) + " mm";
        document.getElementById("lbl-tide").innerText = parseFloat(data.tideLevel).toFixed(2) + " m";
        document.getElementById("lbl-drainage").innerText = parseInt(data.drainageCapacity) + "%";
        document.getElementById("input-bridge").checked = data.bridgeFailure;
        
        // Clock
        document.getElementById("lbl-clock").innerText = "H-" + parseFloat(data.currentTime).toFixed(1) + " Hours";
        if (data.currentTime >= 6.0) {
          document.getElementById("lbl-time-status").innerText = "Simulation Ended.";
        } else if (data.currentTime > 2.0) {
          document.getElementById("lbl-time-status").innerText = "Active evacuations underway!";
        } else {
          document.getElementById("lbl-time-status").innerText = "Delaying departure...";
        }
        
        // Life safety metrics
        const safeAgents = data.agents.filter(a => a.status === "Safe").length;
        const casualties = data.agents.filter(a => a.status === "Casualty").length;
        const arrivedSafeScaled = safeAgents * 250;
        
        document.getElementById("lbl-safescore").innerText = arrivedSafeScaled.toLocaleString() + " Saved";
        document.getElementById("lbl-casualties").innerText = casualties.toLocaleString() + " Lost";
        
        // Handle casualties warning styles
        const cardCas = document.getElementById("card-casualties");
        const iconCasWrap = document.getElementById("icon-casualties-wrapper");
        const iconCas = document.getElementById("icon-casualties");
        const lblCas = document.getElementById("lbl-casualties");
        const tagCas = document.getElementById("state-casualties-tag");
        const valCasTop = document.getElementById("val-casualties-top");
        const iconCasTop = document.getElementById("icon-casualties-top");

        if (valCasTop) valCasTop.innerText = casualties;

        if (casualties > 0) {
          if (cardCas) cardCas.className = "bg-red-950/15 border border-red-500/30 p-4 rounded-xl flex items-center gap-3 transition-all duration-300 animate-pulse";
          if (iconCasWrap) iconCasWrap.className = "p-2.5 bg-red-500/15 border border-red-500/25 rounded-xl shrink-0 transition-all duration-300";
          if (iconCas) iconCas.className = "text-red-400 h-5 w-5 transition-all duration-300";
          if (lblCas) lblCas.className = "text-base text-red-500 font-bold block truncate";
          
          if (tagCas) tagCas.className = "flex items-center gap-2 bg-red-950/20 border border-red-500/30 px-3 py-1.5 rounded-lg text-red-500 font-bold animate-pulse transition-all duration-300";
          if (iconCasTop) iconCasTop.className = "text-red-400 h-3.5 w-3.5 transition-all duration-300";
        } else {
          if (cardCas) cardCas.className = "bg-[#0f172a] border border-slate-800 p-4 rounded-xl flex items-center gap-3 transition-all duration-300";
          if (iconCasWrap) iconCasWrap.className = "p-2.5 bg-slate-500/10 border border-slate-500/20 rounded-xl shrink-0 transition-all duration-300";
          if (iconCas) iconCas.className = "text-slate-400 h-5 w-5 transition-all duration-300";
          if (lblCas) lblCas.className = "text-base text-slate-400 block truncate";
          
          if (tagCas) tagCas.className = "flex items-center gap-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-slate-400 transition-all duration-300";
          if (iconCasTop) iconCasTop.className = "text-slate-400 h-3.5 w-3.5 transition-all duration-300";
        }
        
        // Occupancy metrics
        const totalCapacity = data.centers.reduce((acc, c) => acc + c.capacity, 0);
        const totalOccupied = data.centers.reduce((acc, c) => acc + c.occupancy, 0);
        const totalOccupiedScaled = totalOccupied * 250;
        const totalCapacityScaled = totalCapacity * 250;
        const occupancyPct = Math.round((totalOccupied / totalCapacity) * 100) || 0;
        document.getElementById("lbl-occupancy").innerText = totalOccupiedScaled.toLocaleString() + " / " + totalCapacityScaled.toLocaleString() + " (" + occupancyPct + "%)";
        
        // Rescue patrols
        const activeRescues = data.rescuers.filter(r => r.status !== "Idle").length;
        const totalSaves = data.rescuers.reduce((acc, r) => acc + r.rescuedCount, 0) * 250;
        document.getElementById("lbl-rescue-status").innerText = activeRescues + " Active Missions";
        document.getElementById("lbl-total-rescues").innerText = "Saved by CDRRMC Patrols: " + totalSaves.toLocaleString();
        
        // Trigger redrawing Map
        drawMap();
        
        // Populate dropdown selectors if empty
        populateSelectors();

        if (document.getElementById("input-population")) {
          document.getElementById("input-population").value = data.initialPopulation || 250;
        }
        if (document.getElementById("lbl-population")) {
          document.getElementById("lbl-population").innerText = (data.initialPopulation || 250) + " agents";
        }
        
        updateAgentsSelector();
        
        // Update Inspectors and explanations
        updateInspector();
        updateResearchDashboard();
        updateRescueFleet();
        
        // Toggle play button status
        const playBtn = document.getElementById("btn-toggle-play");
        if (data.isRunning) {
          playBtn.innerHTML = '<i data-lucide="pause" class="h-4 w-4"></i> PAUSE PLAYBACK';
          playBtn.className = "w-full py-2.5 rounded-xl border border-rose-500/30 text-rose-400 bg-rose-500/10 hover:bg-rose-500/20 font-bold tracking-tight flex items-center justify-center gap-2 transition-all cursor-pointer text-xs";
        } else {
          playBtn.innerHTML = '<i data-lucide="play" class="h-4 w-4"></i> START SIMULATOR AUTOMATION';
          playBtn.className = "w-full py-2.5 rounded-xl border border-emerald-500/30 text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/20 font-bold tracking-tight flex items-center justify-center gap-2 transition-all cursor-pointer text-xs";
        }
        
        // update Lucide icons
        if (typeof lucide !== 'undefined' && lucide.createIcons) {
          lucide.createIcons();
        }
        
        // Synced Academic Report Figures
        const academicOverlay = document.getElementById("academic-modal-overlay");
        if (academicOverlay && !academicOverlay.classList.contains("hidden")) {
          renderAcademicFigures();
        }
        
      } catch (err) {
        console.error("Failed to load sim state", err);
      }
    }

    function trackSelectedAgent() {
      const select = document.getElementById("select-active-agent");
      if (!select) return;
      trackedAgentId = select.value;
      const trackedLbl = document.getElementById("lbl-tracked-status");
      
      if (!trackedAgentId) {
        if (trackedLbl) {
          trackedLbl.innerText = "-";
          trackedLbl.className = "text-purple-400 font-bold font-mono";
        }
        return;
      }
      
      const agent = simState.agents.find(a => a.id === trackedAgentId);
      if (agent) {
        if (trackedLbl) {
          trackedLbl.innerText = agent.status.toUpperCase();
        }
        // Pan/Focus map on current coordinates of tracked citizen agent
        let targetPos = clientAgentPositions[trackedAgentId];
        if (targetPos) {
          leafletMap.setView([targetPos.currentLat, targetPos.currentLng], 15);
        }
      } else {
        if (trackedLbl) {
          trackedLbl.innerText = "NOT FOUND";
          trackedLbl.className = "text-slate-500 font-bold font-mono";
        }
      }
    }

    function updateAgentsSelector() {
      const select = document.getElementById("select-active-agent");
      if (!select) return;
      
      const currentSelected = select.value;
      
      if (!simState.agents || simState.agents.length === 0) return;
      
      // Rebuild options list if size/contents do not match current population (plus the header option)
      if (select.children.length <= 1 || (select.children.length - 1) !== simState.agents.length) {
        while (select.children.length > 1) {
          select.removeChild(select.lastChild);
        }
        
        // Sort agents: RescueNeeded -> Stuck -> Evacuating -> Preparing -> Safe -> Casualty
        const sortedAgents = [...simState.agents].sort((a, b) => {
          const score = { "RescueNeeded": 5, "Stuck": 4, "Evacuating": 3, "Preparing": 2, "Safe": 1, "Casualty": 0 };
          return (score[b.status] || 0) - (score[a.status] || 0);
        });
        
        sortedAgents.forEach(a => {
          let opt = document.createElement("option");
          opt.value = a.id;
          opt.innerText = `${a.id} [${a.status}]`;
          if (a.id === currentSelected) opt.selected = true;
          select.appendChild(opt);
        });
      } else {
        // Simple fast update of existing text options
        for (let i = 1; i < select.children.length; i++) {
          const opt = select.children[i];
          const a = simState.agents.find(item => item.id === opt.value);
          if (a) {
            opt.innerText = `${a.id} [${a.status}]`;
          }
        }
      }
      
      // Update label dynamically as agent moves or changes status under active tracking
      if (trackedAgentId) {
        const a = simState.agents.find(item => item.id === trackedAgentId);
        const trackedLbl = document.getElementById("lbl-tracked-status");
        if (trackedLbl) {
          if (a) {
            trackedLbl.innerText = a.status.toUpperCase();
            if (a.status === "RescueNeeded") trackedLbl.className = "text-red-400 font-bold font-mono animate-pulse";
            else if (a.status === "Stuck") trackedLbl.className = "text-orange-400 font-bold font-mono animate-pulse";
            else if (a.status === "Evacuating") trackedLbl.className = "text-yellow-400 font-bold font-mono";
            else if (a.status === "Preparing") trackedLbl.className = "text-purple-400 font-bold font-mono";
            else if (a.status === "Safe") trackedLbl.className = "text-emerald-400 font-bold font-mono";
            else if (a.status === "Casualty") trackedLbl.className = "text-rose-600 font-bold font-mono";
          } else {
            trackedLbl.innerText = "NOT FOUND";
            trackedLbl.className = "text-slate-500 font-bold font-mono";
          }
        }
      }
    }

    function populateSelectors() {
      const select = document.getElementById("select-research-barangay");
      if (!select || select.children.length > 0) return; // already populated
      
      simState.barangays.forEach(b => {
        let opt = document.createElement("option");
        opt.value = b.id;
        opt.innerText = b.name + " (" + b.elevation + "m)";
        select.appendChild(opt);
      });
    }

    async function applyScenario(name) {
      document.getElementById("map-loader").style.opacity = "1";
      clearAgentMarkers();
      await fetch("/api/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario: name })
      });
      setTimeout(() => {
        document.getElementById("map-loader").style.opacity = "0";
        fetchState();
      }, 500);
    }

    async function changeSliders() {
      const rainfall = document.getElementById("input-rainfall").value;
      const tideLevel = document.getElementById("input-tide").value;
      const drainageCapacity = document.getElementById("input-drainage").value;
      const bridgeFailure = document.getElementById("input-bridge").checked;
      const initialPopulation = document.getElementById("input-population").value;
      
      await fetch("/api/set-variables", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rainfall, tideLevel, drainageCapacity, bridgeFailure, initialPopulation })
      });
      fetchState();
    }

    async function togglePlay() {
      await fetch("/api/toggle-run", { method: "POST" });
      fetchState();
    }

    async function stepSim() {
      await fetch("/api/step", { method: "POST" });
      fetchState();
    }

    async function resetSim() {
      await applyScenario(simState ? simState.activeScenarioName : "TS Basyang");
    }

    async function exportCSV() {
      try {
        const response = await fetch("/api/export-csv", { method: "POST" });
        if (!response.ok) {
          console.error("Export API failed:", response.statusText);
          return;
        }
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "simulation_history.csv";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      } catch (err) {
        console.error("Failed to export simulation history CSV:", err);
      }
    }

    function openAcademicModal() {
      const modal = document.getElementById("academic-modal-overlay");
      if (modal) {
        modal.classList.remove("hidden");
        // Hide map container to prevent hardware acceleration overlay bleed
        const mapCont = document.getElementById("leaflet-map-container");
        if (mapCont) {
          mapCont.classList.add("hidden");
        }
        // Populate the barangay selector
        const select = document.getElementById("academic-barangay-select");
        if (select && simState && simState.barangays) {
          select.innerHTML = "";
          simState.barangays.forEach(bg => {
            select.innerHTML += `<option value="${bg.id}">${bg.name}</option>`;
          });
          // Synchronize selection with the main dashboard select
          const mainSelect = document.getElementById("select-research-barangay");
          if (mainSelect) {
            select.value = mainSelect.value || "B1";
          }
        }
        renderAcademicFigures();
        if (typeof lucide !== 'undefined' && lucide.createIcons) {
          lucide.createIcons();
        }
      }
    }

    function closeAcademicModal() {
      const modal = document.getElementById("academic-modal-overlay");
      if (modal) {
        modal.classList.add("hidden");
      }
      // Show map container again
      const mapCont = document.getElementById("leaflet-map-container");
      if (mapCont) {
        mapCont.classList.remove("hidden");
      }
      if (leafletMap) {
        setTimeout(() => { leafletMap.invalidateSize(); }, 150);
      }
    }

    // Export any SVG inside the modal to PNG
    function exportSingleFigure(svgId, filename) {
      const svgEl = document.getElementById(svgId);
      if (!svgEl) {
        console.error("SVG Element not found:", svgId);
        return;
      }
      try {
        const serializer = new XMLSerializer();
        let svgString = serializer.serializeToString(svgEl);
        
        // Ensure namespace is complete
        if (!svgString.match(/^<svg[^>]+xmlns="http:\/\/www\.w3\.org\/2000\/svg"/)) {
          svgString = svgString.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
        }
        
        // In order to support CSS font styling, inject Times New Roman style definitions
        svgString = svgString.replace(/<svg([^>]*)>/, `<svg$1><style>text { font-family: "Times New Roman", Georgia, serif !important; }</style>`);
        
        const svgBlob = new Blob([svgString], { type: "image/svg+xml;charset=utf-8" });
        const URL = window.URL || window.webkitURL || window;
        const blobURL = URL.createObjectURL(svgBlob);
        
        const image = new Image();
        image.onload = function() {
          const canvas = document.createElement("canvas");
          // Multiplier for extremely high publication resolution
          const scale = 3.0;
          const bbox = svgEl.getBoundingClientRect();
          const w = bbox.width || svgEl.viewBox.baseVal.width || 600;
          const h = bbox.height || svgEl.viewBox.baseVal.height || 350;
          
          canvas.width = w * scale;
          canvas.height = h * scale;
          
          const ctx = canvas.getContext("2d");
          ctx.fillStyle = "#ffffff";
          ctx.fillRect(0, 0, canvas.width, canvas.height);
          
          ctx.scale(scale, scale);
          ctx.drawImage(image, 0, 0, w, h);
          
          const pngURL = canvas.toDataURL("image/png");
          const dlLink = document.createElement("a");
          dlLink.href = pngURL;
          dlLink.download = filename;
          document.body.appendChild(dlLink);
          dlLink.click();
          document.body.removeChild(dlLink);
          URL.revokeObjectURL(blobURL);
        };
        image.src = blobURL;
      } catch (err) {
        console.error("Failed to render academic SVG to image file", err);
      }
    }

    function downloadAllFiguresBundle() {
      // Trigger browser download for Figure 1 to 4 sequentially
      exportSingleFigure('academic-fig1-svg', 'Figure1_Comparative_Hazard_Risk.png');
      setTimeout(() => {
        exportSingleFigure('academic-fig2-svg', 'Figure2_State_Trajectories.png');
      }, 300);
      setTimeout(() => {
        exportSingleFigure('academic-fig3-svg', 'Figure3_SpatialTemporal_Heatmap.png');
      }, 600);
      setTimeout(() => {
        exportSingleFigure('academic-fig4-svg', 'Figure4_Localized_4Panel.png');
      }, 900);
    }

    function renderAcademicFigures() {
      if (!simState) return;
      const history = simState.history || [];
      const totalBarangays = simState.barangays || [];

      // =========================================================
      // FIGURE 1: Comparative Flood Hazard Risk (Academic horizontal bar)
      // =========================================================
      const fig1 = document.getElementById("academic-fig1-svg");
      if (fig1) {
        fig1.innerHTML = "";
        
        // Sort descending by flood probability to match academic pattern
        const sorted = [...totalBarangays].sort((a, b) => b.floodProb - a.floodProb);
        const w = 600, h = 320;
        const padL = 140, padR = 50, padT = 30, padB = 40;
        
        let svg = `
          <!-- White background overlay -->
          <rect width="${w}" height="${h}" fill="#ffffff" />
          
          <!-- Outer border -->
          <rect x="1" y="1" width="${w-2}" height="${h-2}" fill="none" stroke="#222222" stroke-width="1.5" />
          
          <!-- Inner plot area boundary -->
          <rect x="${padL}" y="${padT}" width="${w - padL - padR}" height="${h - padT - padB}" fill="none" stroke="#333333" stroke-width="1.2" />
        `;

        // Draw vertical grid lines at 25%, 50%, 75%, 100%
        [0.25, 0.50, 0.75, 1.0].forEach(p => {
          const x = padL + p * (w - padL - padR);
          svg += `
            <line x1="${x}" y1="${padT}" x2="${x}" y2="${h - padB}" stroke="#dddddd" stroke-dasharray="3,3" />
            <text x="${x}" y="${h - padB + 16}" fill="#111111" font-size="10" text-anchor="middle" font-family="'Times New Roman', serif">${(p * 100)}%</text>
            <line x1="${x}" y1="${h - padB}" x2="${x}" y2="${h - padB + 4}" stroke="#333333" stroke-width="1.2" />
          `;
        });
        // 0% mark label
        svg += `
          <text x="${padL}" y="${h - padB + 16}" fill="#111111" font-size="10" text-anchor="middle" font-family="'Times New Roman', serif">0%</text>
          <line x1="${padL}" y1="${h - padB}" x2="${padL}" y2="${h - padB + 4}" stroke="#333333" stroke-width="1.2" />
        `;

        // Render each bar
        const barAreaHeight = h - padT - padB;
        const barSpacing = barAreaHeight / sorted.length;
        const barHeight = barSpacing * 0.65;
        
        sorted.forEach((bg, idx) => {
          const prob = bg.floodProb || 0.0;
          const barW = prob * (w - padL - padR);
          const y = padT + idx * barSpacing + (barSpacing - barHeight)/2;
          
          // Grayscale or highly academic pattern/fill
          // We can use standard dark slate colors which look brilliant for paper printing
          let fill = "#475569"; // default academic slate
          if (prob > 0.6) fill = "#1e293b"; // dense charcoal
          else if (prob > 0.3) fill = "#64748b"; // medium gray
          else fill = "#cbd5e1"; // light silver-gray
          
          svg += `
            <!-- Barangay Name Label -->
            <text x="${padL - 10}" y="${y + barHeight/2 + 3.5}" fill="#000000" font-size="10.5" text-anchor="end" font-weight="bold" font-family="'Times New Roman', serif">${bg.name}</text>
            
            <!-- Horizontal Bar -->
            <rect x="${padL}" y="${y}" width="${Math.max(1, barW)}" height="${barHeight}" fill="${fill}" stroke="#000000" stroke-width="1" />
            
            <!-- Percent text -->
            <text x="${padL + barW + 6}" y="${y + barHeight/2 + 3.5}" fill="#111111" font-size="9.5" text-anchor="start" font-weight="bold" font-family="'Times New Roman', serif">${Math.round(prob * 100)}%</text>
          `;
        });

        // X Axis Title
        svg += `
          <text x="${padL + (w - padL - padR)/2}" y="${h - 8}" fill="#000000" font-size="12" font-weight="bold" text-anchor="middle" font-family="'Times New Roman', serif">Flood Danger Probability Index (TS Basyang Threshold)</text>
        `;
        
        fig1.innerHTML = svg;
      }

      // =========================================================
      // FIGURE 2: Trajectories over Time SVG (Academic format)
      // =========================================================
      const fig2 = document.getElementById("academic-fig2-svg");
      if (fig2) {
        fig2.innerHTML = "";
        
        const w = 600, h = 320;
        const padL = 50, padR = 150, padT = 30, padB = 45;
        const maxVal = simState.agents ? simState.agents.length : 250;
        
        const mapX = (t) => padL + (t / 6.0) * (w - padL - padR);
        const mapY = (v) => h - padB - (v / maxVal) * (h - padT - padB);

        let svg = `
          <!-- Background -->
          <rect width="${w}" height="${h}" fill="#ffffff" />
          <rect x="1" y="1" width="${w-2}" height="${h-2}" fill="none" stroke="#222222" stroke-width="1.5" />
          <rect x="${padL}" y="${padT}" width="${w - padL - padR}" height="${h - padT - padB}" fill="none" stroke="#333333" stroke-width="1.2" />
        `;

        // Horizontal axes grid lines
        [0, Math.round(maxVal * 0.25), Math.round(maxVal * 0.5), Math.round(maxVal * 0.75), maxVal].forEach(val => {
          const y = mapY(val);
          svg += `
            <line x1="${padL}" y1="${y}" x2="${w - padR}" y2="${y}" stroke="#eeeeee" stroke-width="1" />
            <text x="${padL - 8}" y="${y + 3}" fill="#000000" font-size="10" text-anchor="end" font-family="'Times New Roman', serif">${val}</text>
            <line x1="${padL - 4}" y1="${y}" x2="${padL}" y2="${y}" stroke="#333333" stroke-width="1" />
          `;
        });

        // Hour labels
        for (let t = 0; t <= 6; t++) {
          const x = mapX(t);
          svg += `
            <line x1="${x}" y1="${padT}" x2="${x}" y2="${h - padB}" stroke="#eeeeee" stroke-width="1" />
            <text x="${x}" y="${h - padB + 16}" fill="#000000" font-size="10" text-anchor="middle" font-family="'Times New Roman', serif">H-${t}.0</text>
            <line x1="${x}" y1="${h - padB}" x2="${x}" y2="${h - padB + 4}" stroke="#333333" stroke-width="1" />
          `;
        }

        // Draw historic lines
        if (history.length > 0) {
          const drawLine = (key, strokeColor, dashStyle, sWidth) => {
            const points = history.map(pt => {
              const val = pt[key] || 0;
              return `${mapX(pt.time).toFixed(1)},${mapY(val).toFixed(1)}`;
            }).join(" ");
            
            return `<polyline points="${points}" fill="none" stroke="${strokeColor}" stroke-dasharray="${dashStyle}" stroke-width="${sWidth}" stroke-linecap="round" stroke-linejoin="round" />`;
          };

          svg += drawLine("safeCount", "#15803d", "0", 2.5); // Safe: Solid Green
          svg += drawLine("casualtyCount", "#b91c1c", "0", 3.0); // Casualties: Bold solid red
          svg += drawLine("evacuatingCount", "#d97706", "4,2", 2.0); // Active Evacuating: Dash
          svg += drawLine("preparingCount", "#7c3aed", "2,2", 1.8); // Preparing: Dotted Purple
          svg += drawLine("stuckCount", "#475569", "6,3", 1.8); // Stuck: Long Dash
        }

        // Add Legend inside SVG to the right margin area
        const legX = w - padR + 15;
        let legY = padT + 15;
        const legendData = [
          { label: "Safe Evacuated", color: "#15803d", dash: "0", w: "2.5" },
          { label: "Fatal Casualties", color: "#b91c1c", dash: "0", w: "3.0" },
          { label: "Active Evacuation", color: "#d97706", dash: "4,2", w: "2.0" },
          { label: "Preparing in House", color: "#7c3aed", dash: "2,2", w: "1.8" },
          { label: "Stuck / Blocked", color: "#475569", dash: "6,3", w: "1.8" }
        ];

        svg += `
          <!-- Legend Title -->
          <text x="${legX}" y="${legY - 6}" font-size="10.5" font-weight="bold" fill="#000000" font-family="'Times New Roman', serif">State Legend</text>
        `;

        legendData.forEach((item) => {
          svg += `
            <line x1="${legX}" y1="${legY + 4}" x2="${legX + 25}" y2="${legY + 4}" stroke="${item.color}" stroke-dasharray="${item.dash}" stroke-width="${item.w}" />
            <text x="${legX + 32}" y="${legY + 7}" fill="#000000" font-size="9.5" font-family="'Times New Roman', serif">${item.label}</text>
          `;
          legY += 22;
        });

        // Axis Titles
        svg += `
          <text x="${padL + (w - padL - padR)/2}" y="${h - 8}" fill="#000000" font-size="11.5" font-weight="bold" text-anchor="middle" font-family="'Times New Roman', serif">Simulation Dispatch Timeline (hours)</text>
          <text x="14" y="${padT + (h-padT-padB)/2}" fill="#000000" font-size="11.5" font-weight="bold" text-anchor="middle" transform="rotate(-90 14 ${padT + (h-padT-padB)/2})" font-family="'Times New Roman', serif">Simulated Resident Count</text>
        `;

        fig2.innerHTML = svg;
      }

      // =========================================================
      // FIGURE 3: Spatial-Temporal Heatmap Matrix SVG
      // =========================================================
      const fig3 = document.getElementById("academic-fig3-svg");
      if (fig3) {
        fig3.innerHTML = "";
        
        const w = 700, h = 350;
        const padL = 90, padR = 120, padT = 40, padB = 40;
        
        const hours = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0];
        const numCols = hours.length;
        const numRows = totalBarangays.length;
        
        let svg = `
          <!-- Background -->
          <rect width="${w}" height="${h}" fill="#ffffff" />
          <rect x="1" y="1" width="${w-2}" height="${h-2}" fill="none" stroke="#222222" stroke-width="1.5" />
        `;

        const plotW = w - padL - padR;
        const plotH = h - padT - padB;
        const cellW = plotW / numCols;
        const cellH = plotH / numRows;

        // Render Column headers (Hours)
        hours.forEach((hr, colIdx) => {
          const x = padL + colIdx * cellW;
          svg += `
            <text x="${x + cellW/2}" y="${padT - 8}" fill="#000000" font-size="9" font-weight="bold" text-anchor="middle" font-family="'Times New Roman', serif">H-${hr.toFixed(1)}</text>
          `;
        });

        // Render Rows & Heat cells
        totalBarangays.forEach((bg, rowIdx) => {
          const y = padT + rowIdx * cellH;
          
          // Row Label on Left
          svg += `
            <text x="${padL - 8}" y="${y + cellH/2 + 3.5}" fill="#000000" font-size="9.5" text-anchor="end" font-weight="bold" font-family="'Times New Roman', serif">${bg.name}</text>
          `;

          hours.forEach((hr, colIdx) => {
            const x = padL + colIdx * cellW;
            let probVal = 0.0;
            let isForecast = false;
            
            if (hr <= simState.currentTime) {
              const pt = history.find(h => Math.abs(h.time - hr) < 0.15) || history.filter(h => h.time <= hr).pop();
              if (pt) {
                probVal = pt.barangayProbs ? (pt.barangayProbs[bg.id] || 0.0) : 0.0;
              }
            } else {
              isForecast = true;
              // Forecast formula
              const rain = simState.rainfall;
              const time_curve = Math.min(1.0, hr / 4.5);
              const el = bg.elevation;
              let simDepth = 0.0;
              if (bg.riverSourceProximity === "Mandulog") {
                simDepth = Math.max(0.0, ((rain / 100.0) * 1.5 * (hr / 3.0)) - el * 0.12) * time_curve;
              } else if (bg.riverSourceProximity === "Coastal") {
                simDepth = Math.max(0.0, (simState.tideLevel * 0.8 + (rain / 150.0)) * (1.0 + hr * 0.1) - el * 0.15) * time_curve;
              } else if (bg.riverSourceProximity === "Agus") {
                simDepth = Math.max(0.0, ((rain / 100.0) * 1.0 * (hr / 4.0)) - el * 0.1) * time_curve;
              } else {
                simDepth = Math.max(0.0, ((rain / 150.0) * 0.8 * (hr / 2.0)) * (1.1 - simState.drainageCapacity/100.0) - el * 0.08) * time_curve;
              }
              probVal = Math.min(1.0, Math.max(0.0, (simDepth / 0.8)));
            }

            // High aesthetic red/yellow warm thermal scale color mapping 
            let fill = "#fdfaf2"; // near-white baseline
            let strokeCol = "#dddddd";
            let txtColor = "#333333";
            
            if (probVal > 0.0) {
              if (probVal < 0.25) {
                fill = "#fed7aa"; // light orange tint
                txtColor = "#7c2d12";
              } else if (probVal < 0.55) {
                fill = "#fb923c"; // deep mango
                txtColor = "#000000";
              } else if (probVal < 0.85) {
                fill = "#ef4444"; // pure alarm red
                txtColor = "#ffffff";
              } else {
                fill = "#7f1d1d"; // dark crimson
                txtColor = "#ffffff";
              }
            }
            if (isForecast) {
              strokeCol = "#94a3b8"; // slate outline for forecast cells
            }

            const cellText = isForecast ? `F${Math.round(probVal*100)}` : `${Math.round(probVal*100)}%`;

            svg += `
              <rect x="${x}" y="${y}" width="${cellW}" height="${cellH}" fill="${fill}" stroke="${strokeCol}" stroke-width="0.8" />
              <text x="${x + cellW/2}" y="${y + cellH/2 + 3}" fill="${txtColor}" font-size="8" font-weight="bold" text-anchor="middle" font-family="'Times New Roman', serif">${cellText}</text>
            `;
          });
        });

        // Add Scale Color Bar to the right
        const scalX = w - padR + 25;
        const scalY = padT + 20;
        const scalW = 20;
        const scalH = plotH - 40;

        svg += `
          <!-- Gradient Definition -->
          <defs>
            <linearGradient id="academic-heat-grad" x1="0%" y1="100%" x2="0%" y2="0%">
              <stop offset="0%" stop-color="#fdfaf2" />
              <stop offset="25%" stop-color="#fed7aa" />
              <stop offset="50%" stop-color="#fb923c" />
              <stop offset="75%" stop-color="#ef4444" />
              <stop offset="100%" stop-color="#7f1d1d" />
            </linearGradient>
          </defs>
          
          <!-- Heat scale Box -->
          <rect x="${scalX}" y="${scalY}" width="${scalW}" height="${scalH}" fill="url(#academic-heat-grad)" stroke="#000000" stroke-width="1.2" />
          
          <!-- Legend Title & Ticks -->
          <text x="${scalX - 5}" y="${scalY - 10}" fill="#000000" font-size="10" font-weight="bold" text-anchor="start" font-family="'Times New Roman', serif">Danger Profile Scale</text>
          
          <text x="${scalX + scalW + 8}" y="${scalY + 4}" fill="#000000" font-size="9.5" text-anchor="start" font-family="'Times New Roman', serif">1.0 (Critical)</text>
          <line x1="${scalX}" y1="${scalY}" x2="${scalX + scalW + 4}" y2="${scalY}" stroke="#222222" stroke-width="1.2" />
          
          <text x="${scalX + scalW + 8}" y="${scalY + scalH/2 + 4}" fill="#000000" font-size="9.5" text-anchor="start" font-family="'Times New Roman', serif">0.5 (Active)</text>
          <line x1="${scalX}" y1="${scalY + scalH/2}" x2="${scalX + scalW + 4}" y2="${scalY + scalH/2}" stroke="#222222" stroke-width="1.2" />
          
          <text x="${scalX + scalW + 8}" y="${scalY + scalH + 4}" fill="#000000" font-size="9.5" text-anchor="start" font-family="'Times New Roman', serif">0.0 (Baseline)</text>
          <line x1="${scalX}" y1="${scalY + scalH}" x2="${scalX + scalW + 4}" y2="${scalY + scalH}" stroke="#222222" stroke-width="1.2" />
          
          <text x="${scalX - 25}" y="${scalY + scalH + 20}" fill="#475569" font-size="8.5" font-family="'Times New Roman', serif" italic="true">* F-prefix indicates predictive hazard estimation</text>
        `;

        // Inner frame plot boundaries
        svg += `
          <rect x="${padL}" y="${padT}" width="${plotW}" height="${plotH}" fill="none" stroke="#222222" stroke-width="1.5" />
        `;

        // Main labels
        svg += `
          <text x="${padL + plotW/2}" y="${h - 8}" fill="#000000" font-size="12" font-weight="bold" text-anchor="middle" font-family="'Times New Roman', serif">Simulation Spatiotemporal Danger Index Over 6.0 Hours</text>
        `;

        fig3.innerHTML = svg;
      }

      // =========================================================
      // FIGURE 4: 4-Panel Site-Specific Dynamics Profile (Academic unified layout)
      // =========================================================
      const fig4 = document.getElementById("academic-fig4-svg");
      if (fig4) {
        fig4.innerHTML = "";
        
        const bId = document.getElementById("academic-barangay-select").value || "B1";
        const bgInfo = totalBarangays.find(b => b.id === bId) || totalBarangays[0];
        
          if (bgInfo) {
            const w = 800, h = 520;
            const pAl = 45, pAr = 25, pAt = 45, pAb = 40;
            const pAw = 400 - pAl - pAr;
            const pAh = 260 - pAt - pAb;

            let svg = `
              <defs>
                <clipPath id="panel-a-clip">
                  <rect x="${pAl}" y="${pAt}" width="${pAw}" height="${pAh}" />
                </clipPath>
              </defs>
              <!-- Background Sheet -->
              <rect width="${w}" height="${h}" fill="#ffffff" />
              <!-- Border perimeter -->
              <rect x="1" y="1" width="${w-2}" height="${h-2}" fill="none" stroke="#222222" stroke-width="1.5" />
              
              <!-- Division Dividers Lines -->
              <line x1="${w/2}" y1="0" x2="${w/2}" y2="${h}" stroke="#666666" stroke-width="1" stroke-dasharray="4,4" />
              <line x1="0" y1="${h/2}" x2="${w}" y2="${h/2}" stroke="#666666" stroke-width="1" stroke-dasharray="4,4" />
            `;

            // =======================================================
            // PANEL A: Depth dynamics (Top-Left quadrant: 0,0 to 400,260)
            // =======================================================
            const mapX_A = (t) => pAl + (t / 6.0) * pAw;
            const mapY_A = (d) => 260 - pAb - (d / 2.5) * pAh;

          svg += `
            <!-- Panel Tag -->
            <text x="15" y="25" fill="#000000" font-size="14" font-weight="bold" font-family="'Times New Roman', serif">A</text>
            <text x="35" y="25" fill="#000000" font-size="11" font-weight="bold" font-family="'Times New Roman', serif">Simulated Flood Infiltration Depth (Barangay: ${bgInfo.name})</text>
            
            <!-- Plot Boundary -->
            <rect x="${pAl}" y="${pAt}" width="${pAw}" height="${pAh}" fill="none" stroke="#222222" stroke-width="1.2" />
          `;

          // Depth grid-markers and guidelines
          [0.0, 0.5, 1.0, 1.5, 2.0, 2.5].forEach(d => {
            const dy = mapY_A(d);
            svg += `
              <line x1="${pAl}" y1="${dy}" x2="${400 - pAr}" y2="${dy}" stroke="#f3f4f6" stroke-width="1" />
              <text x="${pAl - 6}" y="${dy + 3.5}" fill="#000000" font-size="8.5" text-anchor="end" font-family="'Times New Roman', serif">${d.toFixed(1)}m</text>
              <line x1="${pAl - 3}" y1="${dy}" x2="${pAl}" y2="${dy}" stroke="#333333" stroke-width="1" />
            `;
          });

          // Horizontal hours guidelines A
          for (let h_val = 0; h_val <= 6; h_val += 1) {
            const dx = mapX_A(h_val);
            svg += `
              <line x1="${dx}" y1="${pAt}" x2="${dx}" y2="${260 - pAb}" stroke="#f3f4f6" stroke-width="1" />
              <text x="${dx}" y="${260 - pAb + 13}" fill="#000000" font-size="8.5" text-anchor="middle" font-family="'Times New Roman', serif">H-${h_val}</text>
              <line x1="${dx}" y1="${260 - pAb}" x2="${dx}" y2="${260 - pAb + 3}" stroke="#333333" stroke-width="1" />
            `;
          }

          // Draw baseline threshold line for human drowning danger (0.8m)
          const safetyY = mapY_A(0.8);
          svg += `
            <line x1="${pAl}" y1="${safetyY}" x2="${400 - pAr}" y2="${safetyY}" stroke="#dc2626" stroke-dasharray="3,2" stroke-width="1.2" />
            <text x="${400 - pAr - 8}" y="${safetyY - 5}" fill="#b91c1c" font-size="7.5" font-weight="bold" text-anchor="end" font-family="'Times New Roman', serif">Pedestrian Hazard Baseline (0.8m)</text>
          `;

          // Construct historical line points
          if (history.length > 0) {
            const pointsA = history.map(pt => {
              const depthsObj = pt.barangayDepths || {};
              const d = depthsObj[bId] || 0.0;
              return `${mapX_A(pt.time).toFixed(1)},${mapY_A(d).toFixed(1)}`;
            }).join(" ");
            
            svg += `
              <polyline points="${pointsA}" fill="none" stroke="#581c87" stroke-width="2.2" stroke-linecap="round" clip-path="url(#panel-a-clip)" />
            `;
          }

          svg += `
            <text x="${pAl + pAw/2}" y="${260 - 4}" fill="#000000" font-size="9.5" font-weight="bold" text-anchor="middle" font-family="'Times New Roman', serif">Simulation Time (hours)</text>
            <text x="12" y="${pAt + pAh/2}" fill="#000000" font-size="9.5" font-weight="bold" text-anchor="middle" transform="rotate(-90 12 ${pAt + pAh/2})" font-family="'Times New Roman', serif">Inundation Depth</text>
          `;

          // =======================================================
          // PANEL B: Evacuation outcomes (Top-Right quadrant: 400,0 to 800,260)
          // =======================================================
          const pBl = 445, pBr = 25, pBt = 45, pBb = 40;
          const pBw = 800 - pBl - pBr;
          const pBh = 260 - pBt - pBb;

          svg += `
            <!-- Panel Tag -->
            <text x="415" y="25" fill="#000000" font-size="14" font-weight="bold" font-family="'Times New Roman', serif">B</text>
            <text x="435" y="25" fill="#000000" font-size="11" font-weight="bold" font-family="'Times New Roman', serif">Resident Status Outcome Ratios (${bgInfo.name})</text>
            <rect x="${pBl}" y="${pBt}" width="${pBw}" height="${pBh}" fill="none" stroke="#222222" stroke-width="1.2" />
          `;

          // Compute outcomes for agents originating from active Barangay
          const localAgents = simState.agents ? simState.agents.filter(a => a.sourceBarangayId === bId) : [];
          const totalLocalCount = localAgents.length || 1;
          const safeC = localAgents.filter(a => a.status === "Safe").length;
          const prepC = localAgents.filter(a => a.status === "Preparing").length;
          const evacC = localAgents.filter(a => a.status === "Evacuating").length;
          const stuckC = localAgents.filter(a => a.status === "Stuck").length;
          const deadC = localAgents.filter(a => a.status === "Casualty").length;

          const outcomes = [
            { label: "Safe", val: safeC, fill: "#15803d" },
            { label: "Preparing", val: prepC, fill: "#7c3aed" },
            { label: "Evacuating", val: evacC, fill: "#d97706" },
            { label: "Stuck", val: stuckC, fill: "#475569" },
            { label: "Casualties", val: deadC, fill: "#b91c1c" }
          ];

          // Draw Y scale %
          [0, 25, 50, 75, 100].forEach(pct => {
            const y_pos = 260 - pBb - (pct / 100.0) * pBh;
            svg += `
              <line x1="${pBl}" y1="${y_pos}" x2="${800 - pBr}" y2="${y_pos}" stroke="#f3f4f6" stroke-width="1" />
              <text x="${pBl - 6}" y="${y_pos + 3.5}" fill="#000000" font-size="8.5" text-anchor="end" font-family="'Times New Roman', serif">${pct}%</text>
              <line x1="${pBl - 3}" y1="${y_pos}" x2="${pBl}" y2="${y_pos}" stroke="#333333" stroke-width="1" />
            `;
          });

          // Draw columns
          const numColsB = outcomes.length;
          const colSpacingB = pBw / numColsB;
          const colW_B = colSpacingB * 0.55;

          outcomes.forEach((out, idx) => {
            const pct = (out.val / totalLocalCount) * 100.0;
            const barH = (pct / 100.0) * pBh;
            const x = pBl + idx * colSpacingB + (colSpacingB - colW_B)/2;
            const y = 260 - pBb - barH;

            svg += `
              <!-- Bar -->
              <rect x="${x}" y="${y}" width="${colW_B}" height="${Math.max(1, barH)}" fill="${out.fill}" stroke="#000000" stroke-width="1" />
              <!-- Percentage label -->
              <text x="${x + colW_B/2}" y="${y - 4}" fill="#000000" font-size="8.5" font-weight="bold" text-anchor="middle" font-family="'Times New Roman', serif">${Math.round(pct)}%</text>
              <!-- Label below -->
              <text x="${x + colW_B/2}" y="${260 - pBb + 14}" fill="#000000" font-size="8" font-weight="bold" text-anchor="middle" font-family="'Times New Roman', serif">${out.label}</text>
              <text x="${x + colW_B/2}" y="${260 - pBb + 24}" fill="#475569" font-size="7.5" text-anchor="middle" font-family="'Times New Roman', serif">(n=${out.val})</text>
            `;
          });

          // =======================================================
          // PANEL C: Casualty drowning hazard (Bottom-Left quadrant: 0,260 to 400,520)
          // =======================================================
          const pCl = 45, pCr = 25, pCt = 305, pCb = 40;
          const pCw = 400 - pCl - pCr;
          const pCh = 520 - pCt - pCb;

          const mapX_C = (depth) => pCl + (depth / 2.5) * pCw;
          const mapY_C = (hazProb) => 520 - pCb - hazProb * pCh;

          svg += `
            <!-- Panel Tag -->
            <text x="15" y="285" fill="#000000" font-size="14" font-weight="bold" font-family="'Times New Roman', serif">C</text>
            <text x="35" y="285" fill="#000000" font-size="11" font-weight="bold" font-family="'Times New Roman', serif">Drowning Mortality Risk Profile vs. Water Level</text>
            <rect x="${pCl}" y="${pCt}" width="${pCw}" height="${pCh}" fill="none" stroke="#222222" stroke-width="1.2" />
          `;

          // Gridlines Y probability
          [0.0, 0.25, 0.50, 0.75, 1.0].forEach(p => {
            const cy = mapY_C(p);
            svg += `
              <line x1="${pCl}" y1="${cy}" x2="${400 - pCr}" y2="${cy}" stroke="#f3f4f6" stroke-width="1" />
              <text x="${pCl - 6}" y="${cy + 3.5}" fill="#000000" font-size="8.5" text-anchor="end" font-family="'Times New Roman', serif">${Math.round(p*100)}%</text>
              <line x1="${pCl - 3}" y1="${cy}" x2="${pCl}" y2="${cy}" stroke="#333333" stroke-width="1" />
            `;
          });

          // Depth intervals X Axis
          [0.0, 0.5, 1.0, 1.5, 2.0, 2.5].forEach(d => {
            const cx = mapX_C(d);
            svg += `
              <line x1="${cx}" y1="${pCt}" x2="${cx}" y2="${520 - pCb}" stroke="#f3f4f6" stroke-width="1" />
              <text x="${cx}" y="${520 - pCb + 13}" fill="#000000" font-size="8.5" text-anchor="middle" font-family="'Times New Roman', serif">${d.toFixed(1)}m</text>
              <line x1="${cx}" y1="${520 - pCb}" x2="${cx}" y2="${520 - pCb + 3}" stroke="#333333" stroke-width="1" />
            `;
          });

          // Draw Sigmoid Hazard Curve
          const pointsC = [];
          for (let d = 0; d <= 2.5; d += 0.1) {
            // Sigmoid: 1 / (1 + exp(-4 * (d - 1.1)))
            const p = 1.0 / (1.0 + Math.exp(-4.5 * (d - 1.1)));
            pointsC.push(`${mapX_C(d).toFixed(1)},${mapY_C(p).toFixed(1)}`);
          }
          svg += `
            <polyline points="${pointsC.join(" ")}" fill="none" stroke="#b91c1c" stroke-width="2.5" />
          `;

          svg += `
            <text x="${pCl + pCw/2}" y="${520 - 4}" fill="#000000" font-size="9.5" font-weight="bold" text-anchor="middle" font-family="'Times New Roman', serif">Flood Inundation Depth (m)</text>
            <text x="12" y="${pCt + pCh/2}" fill="#000000" font-size="9.5" font-weight="bold" text-anchor="middle" transform="rotate(-90 12 ${pCt + pCh/2})" font-family="'Times New Roman', serif">Probability of Fatal Drowning</text>
          `;

          // =======================================================
          // PANEL D: Local Geomorphology Table (Bottom-Right quadrant: 400,260 to 800,520)
          // =======================================================
          svg += `
            <!-- Panel Tag -->
            <text x="415" y="285" fill="#000000" font-size="14" font-weight="bold" font-family="'Times New Roman', serif">D</text>
            <text x="435" y="285" fill="#000000" font-size="11" font-weight="bold" font-family="'Times New Roman', serif">Site-Specific Hydrologics & Demographics Table</text>
          `;

          // Three-Line Table rendering coordinates
          const tx = 430;
          const ty = 310;
          const tWidth = 345;
          const rowHeight = 25;

          const h_dangerVal = Math.round(bgInfo.floodProb * 100);
          const hazardText = h_dangerVal > 60 ? "CRITICAL HAZARD ZONE" : (h_dangerVal > 30 ? "MODERATE HAZARD" : "SECURE RETENTION GROUND");

          const tableRows = [
            { field: "BARANGAY ID DESIGNATOR", value: bgInfo.id },
            { field: "TOPOLOGICAL ELEVATION BASE", value: `${bgInfo.elevation.toFixed(1)} meters above MSL` },
            { field: "RIVER REACH BASIN CONDUIT", value: bgInfo.riverSourceProximity || "Interior" },
            { field: "MODEL MONTE CARLO DAMAGE", value: `${h_dangerVal}% Potential Overflow` },
            { field: "CALCULATED STRUCTURAL THRESHOLD", value: hazardText }
          ];

          // Draw Three-Line Table borders (Standard scholastic scientific tables!)
          svg += `
            <!-- Top Thick Line -->
            <line x1="${tx}" y1="${ty}" x2="${tx + tWidth}" y2="${ty}" stroke="#000000" stroke-width="1.8" />
            <!-- Header Text -->
            <text x="${tx + 4}" y="${ty + 15}" fill="#000000" font-size="10" font-weight="bold" font-family="'Times New Roman', serif">GEOMORPHOLOGY PROPERTY SCHEMA</text>
            <text x="${tx + tWidth - 4}" y="${ty + 15}" fill="#000000" font-size="10" font-weight="bold" text-anchor="end" font-family="'Times New Roman', serif">MODEL ATTRIBUTE VALUE</text>
            <!-- Middle Header Border line -->
            <line x1="${tx}" y1="${ty + 22}" x2="${tx + tWidth}" y2="${ty + 22}" stroke="#000000" stroke-width="1.2" />
          `;

          // Table Rows values
          tableRows.forEach((row, r_idx) => {
            const ry = ty + 22 + (r_idx + 1) * rowHeight;
            const bgTextCol = row.field.includes("THRESHOLD") && h_dangerVal > 60 ? "#991b1b" : "#111111";
            svg += `
              <text x="${tx + 4}" y="${ry - 8}" fill="#334155" font-size="9" font-weight="bold" font-family="'Times New Roman', serif">${row.field}</text>
              <text x="${tx + tWidth - 4}" y="${ry - 8}" fill="${bgTextCol}" font-size="9" font-weight="bold" text-anchor="end" font-family="'Times New Roman', serif">${row.value}</text>
              <!-- Light interior row helper divider -->
              <line x1="${tx}" y1="${ry}" x2="${tx + tWidth}" y2="${ry}" stroke="#eeeeee" stroke-width="0.8" />
            `;
          });

          // Draw bottom thick border
          const finalTableY = ty + 22 + (tableRows.length) * rowHeight + 10;
          svg += `
            <line x1="${tx}" y1="${finalTableY}" x2="${tx + tWidth}" y2="${finalTableY}" stroke="#000000" stroke-width="1.8" />
            <text x="${tx + 4}" y="${finalTableY + 14}" fill="#475569" font-size="8" font-family="'Times New Roman', serif" italic="true">Compiled in live sync with Active Simulation agent database.</text>
          `;

          fig4.innerHTML = svg;
        }
      }
    }

    function drawMap() {
      if (!simState) return;
      
      // Ensure Leaflet is initialized
      initLeafletMap();
      
      drawLeafletMap();
    }

    function drawLeafletMap() {
      if (!leafletMap || !simState) return;
      
      leafletRoadsGroup.clearLayers();
      leafletMarkersGroup.clearLayers();
      
      const activePathNodes = window.computedActivePath || [];
      
      // 1. Plot Roads with Flood state levels and Active path styling overlays
      simState.roads.forEach(r => {
        const fromBg = simState.barangays.find(b => b.id === r.from);
        const toBg = simState.barangays.find(b => b.id === r.to);
        if (!fromBg || !toBg) return;
        
        let strokeColor = "#334155";
        let isHighlighted = false;
        
        for (let j = 0; j < activePathNodes.length - 1; j++) {
          if ((activePathNodes[j] === r.from && activePathNodes[j+1] === r.to) ||
              (activePathNodes[j] === r.to && activePathNodes[j+1] === r.from)) {
            isHighlighted = true;
          }
        }
        
        if (r.currentDepth > 0.95) {
          strokeColor = "#ef4444"; // red block
        } else if (r.currentDepth > 0.4) {
          strokeColor = "#f59e0b"; // amber deep flow
        } else {
          strokeColor = "#0ea5e9"; // standard dry road teal-sky
        }
        
        const lineWeight = r.isBridge ? 6 : 4.5;
        const poly = L.polyline([[fromBg.lat, fromBg.lng], [toBg.lat, toBg.lng]], {
          color: strokeColor,
          weight: lineWeight,
          opacity: 0.85,
          dashArray: r.isBridge ? "12, 6" : null
        });
        
        poly.on('click', () => {
          inspectElement('road', r.id);
        });
        
        poly.bindTooltip(`<strong>${r.name}</strong><br/>Status: ${r.currentDepth > 0 ? r.currentDepth.toFixed(1) + 'm water' : 'Dry road'}`, { sticky: true });
        leafletRoadsGroup.addLayer(poly);
        
        if (isHighlighted) {
          // Purple pulsing road highlight underlay
          const pulsePoly = L.polyline([[fromBg.lat, fromBg.lng], [toBg.lat, toBg.lng]], {
            color: "#d8b4fe",
            weight: lineWeight + 3,
            opacity: 0.95,
            dashArray: "10, 6"
          });
          pulsePoly.on('click', () => {
            inspectElement('road', r.id);
          });
          leafletRoadsGroup.addLayer(pulsePoly);
        }
      });
      
      // 2. Plot Barangays with scaled background representations
      simState.barangays.forEach(b => {
        let radiusMeters = 140 + (b.population / 45); // proportional population footprint size scale
        let fillValue = "#1e293b";
        let strokeValue = "#64748b";
        let fillOpacity = 0.55;
        
        if (b.floodDepth > 0.95) {
          fillValue = "#ef4444";
          strokeValue = "#fca5a5";
          fillOpacity = 0.75;
        } else if (b.floodDepth > 0.4) {
          fillValue = "#f59e0b";
          strokeValue = "#fde047";
          fillOpacity = 0.65;
        } else {
          if (b.id === selectedNodeId) {
            fillValue = "#a855f7";
            strokeValue = "#d8b4fe";
            fillOpacity = 0.75;
          }
        }
        
        const circle = L.circle([b.lat, b.lng], {
          color: strokeValue,
          fillColor: fillValue,
          fillOpacity: fillOpacity,
          weight: b.id === selectedNodeId ? 4 : 2,
          radius: radiusMeters
        });
        
        circle.bindTooltip(`<b>Barangay ${b.name}</b><br/>Flood Level: ${b.floodDepth > 0 ? b.floodDepth.toFixed(1) + 'm' : 'Dry'}`, { sticky: true });
        circle.on('click', () => {
          inspectElement('barangay', b.id);
        });
        
        leafletMarkersGroup.addLayer(circle);
      });
      
      // 3. Plot Evacuation Centers
      simState.centers.forEach(c => {
        let isSelected = selectedNodeId === c.id;
        let fillValue = isSelected ? "#a855f7" : "#10b981";
        let strokeValue = isSelected ? "#34d399" : "#34d399";
        
        const htmlIconStr = `
          <div class="flex items-center justify-center cursor-pointer transition-transform hover:scale-125" style="width:28px; height:28px;">
            <svg viewBox="0 0 24 24" class="w-full h-full drop-shadow-lg" xmlns="http://www.w3.org/2000/svg">
              <polygon points="12,2 22,6 20,18 12,22 4,18 2,6" fill="${fillValue}" stroke="${strokeValue}" stroke-width="2.5" />
              <path d="M12 7 L12 17 M7 12 L17 12" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" />
            </svg>
          </div>
        `;
        
        const divIcon = L.divIcon({
          html: htmlIconStr,
          className: 'custom-leaflet-shelter',
          iconSize: [28, 28],
          iconAnchor: [14, 14]
        });
        
        const marker = L.marker([c.lat, c.lng], { icon: divIcon });
        const occupancyPercent = Math.round((c.occupancy / c.capacity) * 100) || 0;
        
        marker.bindTooltip(`<b>SHELTER: ${c.name}</b><br/>Occupancy: ${(c.occupancy * 250).toLocaleString()} / ${(c.capacity * 250).toLocaleString()} (${occupancyPercent}%)`, { sticky: true });
        marker.on('click', () => {
          inspectElement('center', c.id);
        });
        leafletMarkersGroup.addLayer(marker);
      });

      // 4. Plot Active Simulated Citizens Evacuation Progress (Canvas circle markers)
      if (simState.agents && simState.agents.length > 0) {
        // Prune stale markers first
        const activeAgentIds = new Set(simState.agents.map(a => a.id));
        for (const id in leafletAgentMarkers) {
          if (!activeAgentIds.has(id)) {
            leafletAgentsGroup.removeLayer(leafletAgentMarkers[id]);
            delete leafletAgentMarkers[id];
            delete clientAgentPositions[id];
          }
        }

        simState.agents.forEach(a => {
          let latVal = 8.225;
          let lngVal = 124.248;
          let nameLabel = "";
          
          if (a.status === "Safe") {
            const centerItem = simState.centers.find(c => c.id === a.targetCenterId);
            if (centerItem) {
              latVal = centerItem.lat;
              lngVal = centerItem.lng;
              nameLabel = "Sheltered at " + centerItem.name;
            } else {
              const brgyItem = simState.barangays.find(b => b.id === a.currentBarangayId);
              if (brgyItem) {
                latVal = brgyItem.lat;
                lngVal = brgyItem.lng;
                nameLabel = "Barangay " + brgyItem.name;
              }
            }
          } else {
            const brgyItem = simState.barangays.find(b => b.id === a.currentBarangayId);
            if (brgyItem) {
              latVal = brgyItem.lat;
              lngVal = brgyItem.lng;
              nameLabel = "Barangay " + brgyItem.name;
            }
          }
          
          // Apply structured deterministic coordinates offset to cluster dots nicely
          const idNum = parseInt(a.id.replace("CIV-", "")) || 0;
          const jitterLat = Math.sin(idNum * 12.9898) * 0.0008;
          const jitterLng = Math.cos(idNum * 78.233) * 0.0008;
          const finalLat = latVal + jitterLat;
          const finalLng = lngVal + jitterLng;
          
          let markerColor = "#a1a1aa";
          let radius = 2.5;
          let fillOpacity = 0.8;
          let isPulsing = false;
          
          if (a.status === "Safe") {
            markerColor = "#10b981"; // elegant green
            radius = 2.0; 
            fillOpacity = 0.55;
          } else if (a.status === "Evacuating") {
            markerColor = "#eab308"; // walking state yellow
            radius = 3.0; 
            fillOpacity = 0.9;
          } else if (a.status === "RescueNeeded") {
            markerColor = "#ef4444"; // red help required
            radius = 4.2;
            fillOpacity = 1.0;
            isPulsing = true;
          } else if (a.status === "Stuck") {
            markerColor = "#f97316"; // orange stranded delay
            radius = 3.5;
            fillOpacity = 0.9;
          } else if (a.status === "Casualty") {
            markerColor = "#4b5563"; // gray casualty
            radius = 2.0;
            fillOpacity = 0.4;
          }

          let isTracked = (a.id === trackedAgentId);
          if (isTracked) {
            markerColor = "#38bdf8"; // bright sky blue tracking color
            radius = radius + 5.5; 
            fillOpacity = 1.0;
            isPulsing = true;
          }

          // Register or update target coordinates for sliding animation flow
          if (!clientAgentPositions[a.id]) {
            clientAgentPositions[a.id] = {
              currentLat: finalLat,
              currentLng: finalLng,
              targetLat: finalLat,
              targetLng: finalLng
            };
          } else {
            clientAgentPositions[a.id].targetLat = finalLat;
            clientAgentPositions[a.id].targetLng = finalLng;
          }
          
          let marker = leafletAgentMarkers[a.id];
          if (!marker) {
            marker = L.circleMarker([clientAgentPositions[a.id].currentLat, clientAgentPositions[a.id].currentLng], {
              radius: radius,
              color: isPulsing ? (isTracked ? "#1edf92" : "#ffffff") : markerColor,
              fillColor: markerColor,
              fillOpacity: fillOpacity,
              weight: isPulsing ? (isTracked ? 3.0 : 1.5) : 1,
              opacity: fillOpacity
            });
            
            marker.on('click', () => {
              // Click also highlights the agent in tracker!
              document.getElementById("select-active-agent").value = a.id;
              trackSelectedAgent();
              if (a.status !== "Safe" && a.currentBarangayId) {
                inspectElement('barangay', a.currentBarangayId);
              } else if (a.targetCenterId) {
                inspectElement('center', a.targetCenterId);
              }
            });
            
            marker.addTo(leafletAgentsGroup);
            leafletAgentMarkers[a.id] = marker;
          } else {
            // Update in-place styling options to maximize browser FPS
            marker.setStyle({
              radius: radius,
              color: isPulsing ? (isTracked ? "#1edf92" : "#ffffff") : markerColor,
              fillColor: markerColor,
              fillOpacity: fillOpacity,
              weight: isPulsing ? (isTracked ? 3.0 : 1.5) : 1,
              opacity: fillOpacity
            });
          }
          
          marker.bindTooltip(`<b>${a.id}</b><br/>Status: <span class="uppercase font-bold">${a.status}</span><br/>Location: ${nameLabel}`, { sticky: true });
        });
      }

      // 5. Plot Specialty Search & Rescue (SAR) Fleet Patrols moving in real-time
      if (simState.rescuers && simState.rescuers.length > 0) {
        // Prune stale rescuers first
        const activeRescuerIds = new Set(simState.rescuers.map(r => r.id));
        for (const id in leafletRescuerMarkers) {
          if (!activeRescuerIds.has(id)) {
            leafletRescuersGroup.removeLayer(leafletRescuerMarkers[id]);
            delete leafletRescuerMarkers[id];
            delete clientRescuerPositions[id];
          }
        }

        simState.rescuers.forEach(r => {
          const brgyItem = simState.barangays.find(b => b.id === r.barangayId);
          if (!brgyItem) return;
          
          let latVal = brgyItem.lat;
          let lngVal = brgyItem.lng;
          
          const idNum = parseInt(r.id.replace("R", "")) || 0;
          const finalLat = latVal + 0.001 * (idNum - 3);
          const finalLng = lngVal + 0.001 * (idNum - 3);
          
          let isMoving = r.status !== "Idle";
          let pulseClass = isMoving ? "animate-pulse" : "";
          let iconColor = isMoving ? "#ef4444" : "#3b82f6"; // urgent red for dispatches, blue standby
          let strokeColor = isMoving ? "#ffe4e6" : "#dbeafe";

          // Register or update target coordinates for search and rescue vehicles
          if (!clientRescuerPositions[r.id]) {
            clientRescuerPositions[r.id] = {
              currentLat: finalLat,
              currentLng: finalLng,
              targetLat: finalLat,
              targetLng: finalLng
            };
          } else {
            clientRescuerPositions[r.id].targetLat = finalLat;
            clientRescuerPositions[r.id].targetLng = finalLng;
          }
          
          const rescIconHtml = `
            <div class="flex items-center justify-center cursor-pointer transition-all hover:scale-125" style="width:34px; height:34px; filter: drop-shadow(0 0 5px ${iconColor});">
              <div class="w-full h-full rounded-full border-2 bg-[#090d16] flex items-center justify-center relative" style="border-color: ${strokeColor};">
                <span class="absolute w-2.5 h-2.5 rounded-full ${isMoving ? 'animate-ping' : ''}" style="background-color: ${iconColor};"></span>
                <svg viewBox="0 0 24 24" style="color: ${iconColor}; fill: none; stroke: currentColor; stroke-width: 2.2; width: 18px; height: 18px;" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                </svg>
              </div>
            </div>
          `;

          let marker = leafletRescuerMarkers[r.id];
          if (!marker) {
            const divIcon = L.divIcon({
              html: rescIconHtml,
              className: 'custom-leaflet-rescuer ' + pulseClass,
              iconSize: [34, 34],
              iconAnchor: [17, 17]
            });

            marker = L.marker([clientRescuerPositions[r.id].currentLat, clientRescuerPositions[r.id].currentLng], { icon: divIcon });
            marker.on('click', () => {
              inspectElement('barangay', r.barangayId);
            });
            marker.addTo(leafletRescuersGroup);
            leafletRescuerMarkers[r.id] = marker;
          } else {
            // Update the divicon HTML in-place
            const divIcon = L.divIcon({
              html: rescIconHtml,
              className: 'custom-leaflet-rescuer ' + pulseClass,
              iconSize: [34, 34],
              iconAnchor: [17, 17]
            });
            marker.setIcon(divIcon);
          }
          
          marker.bindTooltip(`<b>EMERGENCY VEHICLE: ${r.name}</b><br/>Status: <span class="uppercase text-amber-450 font-bold">${r.status}</span><br/>Location Centroid: ${brgyItem.name}<br/>Escorted Saves: ${(r.rescuedCount * 250).toLocaleString()} citizens`, { sticky: true });
        });
      }
    }

    function inspectElement(type, id) {
      selectedNodeId = id;
      updateInspector();
      drawMap();
    }

    function updateInspector() {
      if (!simState) return;
      
      // seek element
      let item = simState.barangays.find(b => b.id === selectedNodeId);
      let isCenter = false;
      let isRoad = false;
      
      if (!item) {
        item = simState.centers.find(c => c.id === selectedNodeId);
        if (item) isCenter = true;
      }
      
      if (!item) {
        item = simState.roads.find(r => r.id === selectedNodeId);
        if (item) isRoad = true;
      }
      
      if (!item) {
        // default back
        item = simState.barangays[0];
      }
      
      const titleBox = document.getElementById("inspect-title");
      const elevationBox = document.getElementById("inspect-elevation");
      const popBox = document.getElementById("inspect-population");
      const proximityBox = document.getElementById("inspect-proximity");
      const depthBox = document.getElementById("inspect-depth");
      const riskLabel = document.getElementById("inspect-risk-label");
      const probBar = document.getElementById("inspect-prob-bar");
      const probTxt = document.getElementById("inspect-prob-txt");
      
      if (isCenter) {
        titleBox.innerText = item.name;
        elevationBox.innerText = item.elevation + " meters";
        popBox.innerText = "Capacity: " + item.capacity;
        proximityBox.innerText = "Available: " + (item.isAvailable ? "YES" : "NO");
        proximityBox.className = "px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 uppercase";
        
        const scaledOcc = item.occupancy * 250;
        const scaledCap = item.capacity * 250;
        depthBox.innerText = item.occupancy + " units";
        riskLabel.innerText = "Saved: " + scaledOcc.toLocaleString() + " citizens";
        
        const pct = Math.round((item.occupancy / item.capacity) * 100) || 0;
        probBar.style.width = pct + "%";
        probTxt.innerText = pct + "% full";
      } else if (isRoad) {
        titleBox.innerText = item.name;
        elevationBox.innerText = item.baselineElevation + " meters";
        popBox.innerText = "Length: " + item.distance + " km";
        proximityBox.innerText = "Type: " + (item.isBridge ? "Bridge segment" : "Highway Trunk");
        proximityBox.className = "px-2 py-0.5 rounded text-[10px] font-bold bg-[#a855f7]/10 text-purple-400 uppercase";
        
        depthBox.innerText = item.currentDepth + " meters";
        riskLabel.innerText = "Status: " + item.status;
        
        const prob = Math.round((item.passabilityProb) * 100);
        probBar.style.width = prob + "%";
        probTxt.innerText = prob + "% Open chance";
      } else {
        // Barangay node
        titleBox.innerText = item.name + " Barangay";
        elevationBox.innerText = item.elevation + " meters";
        popBox.innerText = "Census: " + item.population.toLocaleString();
        
        proximityBox.innerText = "Water Channel: " + item.riverSourceProximity;
        proximityBox.className = "px-2 py-0.5 rounded text-[10px] font-bold bg-[#38bdf8]/10 text-sky-400 uppercase";
        
        depthBox.innerText = item.floodDepth + " meters";
        if (item.floodDepth > 0.95) {
          riskLabel.innerText = "Severe / Flash alert";
          riskLabel.className = "text-[10px] text-rose-500 font-mono font-bold animate-pulse";
        } else if (item.floodDepth > 0.4) {
          riskLabel.innerText = "Minor inundation";
          riskLabel.className = "text-[10px] text-amber-500 font-mono";
        } else {
          riskLabel.innerText = "Safe Dry Land";
          riskLabel.className = "text-[10px] text-emerald-400 font-mono";
        }
        
        const prob = Math.round((item.floodProb) * 100);
        probBar.style.width = prob + "%";
        probTxt.innerText = prob + "% flooded prob";
      }
    }

    function updateResearchDashboard() {
      if (!simState) return;

      // Populate selector for Fig 4 if needed
      populateSelectors();

      // ==========================================
      // 1. Figure 1: Overall Comparative Barangay Flood Risk
      // ==========================================
      const f1Container = document.getElementById("fig1-bar-container");
      if (f1Container) {
        f1Container.innerHTML = "";
        // Sort descending by flood probability
        const sortedBrgys = [...simState.barangays].sort((a, b) => b.floodProb - a.floodProb);
        sortedBrgys.forEach(b => {
          const prob = Math.round(b.floodProb * 100);
          const barColor = prob > 60 ? "bg-rose-500" : (prob > 30 ? "bg-amber-500" : "bg-emerald-500");
          const textColor = prob > 60 ? "text-rose-400" : (prob > 30 ? "text-amber-400" : "text-emerald-400");
          
          f1Container.innerHTML += `
            <div class="flex items-center gap-3 text-xs leading-none">
              <span class="w-16 truncate font-mono text-[10px] text-slate-400 text-left">${b.name}</span>
              <div class="flex-1 bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-900/65">
                <div class="${barColor} h-full rounded transition-all duration-300" style="width: ${prob}%"></div>
              </div>
              <span class="w-8 text-[11px] text-right font-black ${textColor} font-mono">${prob}%</span>
            </div>
          `;
        });
      }

      // Ensure history exists
      const history = simState.history || [];

      // ==========================================
      // 2. Figure 2: Trajectories over Time SVG
      // ==========================================
      const f2Svg = document.getElementById("fig2-svg");
      if (f2Svg) {
        f2Svg.innerHTML = "";
        
        const width = 450;
        const height = 200;
        const padLeft = 40;
        const padRight = 15;
        const padTop = 15;
        const padBottom = 25;
        const maxVal = simState.agents ? simState.agents.length : 250;

        const mapX = (t) => padLeft + (t / 6.0) * (width - padLeft - padRight);
        const mapY = (v) => height - padBottom - (v / maxVal) * (height - padTop - padBottom);

        // Draw axes & grid grids
        let svgContent = `
          <!-- grid lines -->
          <line x1="${padLeft}" y1="${padTop}" x2="${width - padRight}" y2="${padTop}" stroke="#1e293b" stroke-dasharray="3,3" />
          <line x1="${padLeft}" y1="${mapY(maxVal * 0.5)}" x2="${width - padRight}" y2="${mapY(maxVal * 0.5)}" stroke="#1e293b" stroke-dasharray="3,3" />
          <line x1="${padLeft}" y1="${height - padBottom}" x2="${width - padRight}" y2="${height - padBottom}" stroke="#334155" />
          <line x1="${padLeft}" y1="${padTop}" x2="${padLeft}" y2="${height - padBottom}" stroke="#334155" />
        `;

        // Vertical hour grid lines
        for (let h = 0; h <= 6; h++) {
          const x = mapX(h);
          svgContent += `
            <line x1="${x}" y1="${padTop}" x2="${x}" y2="${height - padBottom}" stroke="#1e293b" stroke-dasharray="2,2" />
            <text x="${x}" y="${height - 10}" fill="#94a3b8" font-size="8" text-anchor="middle">H-${h}</text>
          `;
        }

        // Horizontal pop markers
        [0, Math.round(maxVal * 0.5), maxVal].forEach(val => {
          const y = mapY(val);
          svgContent += `
            <text x="${padLeft - 8}" y="${y + 3}" fill="#94a3b8" font-size="8" text-anchor="end">${(val * 250).toLocaleString()}</text>
          `;
        });

        if (history.length > 0) {
          // Dynamic polys
          const buildPolyline = (key, stroke, widthVal) => {
            const points = history.map(pt => {
              let val = pt[key] || 0;
              if (key === "stuckCount") val = pt.stuckCount;
              return `${mapX(pt.time).toFixed(1)},${mapY(val).toFixed(1)}`;
            }).join(" ");
            return `<polyline points="${points}" fill="none" stroke="${stroke}" stroke-width="${widthVal}" stroke-linecap="round" />`;
          };

          svgContent += buildPolyline("safeCount", "#10b981", 2.2);
          svgContent += buildPolyline("casualtyCount", "#f43f5e", 2.2);
          svgContent += buildPolyline("evacuatingCount", "#eab308", 1.8);
          svgContent += buildPolyline("preparingCount", "#a855f7", 1.5);
          svgContent += buildPolyline("stuckCount", "#fb923c", 1.8);
        }

        f2Svg.innerHTML = svgContent;
      }

      // ==========================================
      // 3. Figure 3: Spatial-Temporal Heatmap Matrix
      // ==========================================
      const heatmapContainer = document.getElementById("fig3-heatmap-table");
      if (heatmapContainer) {
        heatmapContainer.innerHTML = "";
        
        // Define X hours columns (steps of 0.5)
        const hours = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0];
        
        // Header Row
        let headerHtml = `<div class="flex items-center border-b border-slate-900 pb-1.5 mb-1 text-[9px] font-mono text-slate-500 font-extrabold uppercase">
          <div class="w-16 shrink-0">Location</div>
          <div class="flex-1 grid grid-cols-13 gap-1 pl-2">
        `;
        hours.forEach(hr => {
          headerHtml += `<div class="text-center">${hr.toFixed(1)}h</div>`;
        });
        headerHtml += "</div></div>";
        heatmapContainer.innerHTML = headerHtml;

        // Content Rows per Barangay
        simState.barangays.forEach(bg => {
          let rowHtml = `
            <div class="flex items-center py-1 border-b border-slate-900/40 text-[10px] hover:bg-slate-900/30 rounded px-1 transition-all">
              <div class="w-16 shrink-0 font-mono text-slate-400 font-bold truncate">${bg.name}</div>
              <div class="flex-1 grid grid-cols-13 gap-1 pl-2">
          `;

          hours.forEach(hr => {
            // Find historic point for nearest time step less than or equal to current time
            let cellBg = "bg-slate-950/40 border border-slate-900/20";
            let hoverStatTxt = "Future Step";
            let probValText = "";

            if (hr <= simState.currentTime) {
              const pt = history.find(h => Math.abs(h.time - hr) < 0.15) || history.filter(h => h.time <= hr).pop();
              if (pt) {
                const probVal = pt.barangayProbs ? (pt.barangayProbs[bg.id] || 0.0) : 0.0;
                probValText = `${Math.round(probVal * 100)}%`;
                
                // Color ramp mapping
                if (probVal === 0.0) {
                  cellBg = "bg-[#0c1221]";
                } else if (probVal < 0.25) {
                  cellBg = "bg-violet-950/60";
                } else if (probVal < 0.55) {
                  cellBg = "bg-amber-950/60 border border-amber-600/30 text-amber-300";
                } else if (probVal < 0.85) {
                  cellBg = "bg-rose-950/70 border border-rose-500/40 text-rose-300";
                } else {
                  cellBg = "bg-red-600/90 text-white font-black";
                }
                hoverStatTxt = `${Math.round(probVal * 100)}% Danger`;
              } else {
                cellBg = "bg-[#0c1221]";
              }
            } else {
              // Forecast estimations using formulas
              const rain = simState.rainfall;
              const time_curve = Math.min(1.0, hr / 4.5);
              const el = bg.elevation;
              let simDepth = 0.0;
              if (bg.riverSourceProximity === "Mandulog") {
                simDepth = Math.max(0.0, ((rain / 100.0) * 1.5 * (hr / 3.0)) - el * 0.12) * time_curve;
              } else if (bg.riverSourceProximity === "Coastal") {
                simDepth = Math.max(0.0, (simState.tideLevel * 0.8 + (rain / 150.0)) * (1.0 + hr * 0.1) - el * 0.15) * time_curve;
              } else if (bg.riverSourceProximity === "Agus") {
                simDepth = Math.max(0.0, ((rain / 100.0) * 1.0 * (hr / 4.0)) - el * 0.1) * time_curve;
              } else {
                simDepth = Math.max(0.0, ((rain / 150.0) * 0.8 * (hr / 2.0)) * (1.1 - simState.drainageCapacity/100.0) - el * 0.08) * time_curve;
              }
              const forecastProb = Math.min(1.0, Math.max(0.0, (simDepth / 0.8)));
              probValText = `F${Math.round(forecastProb * 100)}`;
              if (forecastProb > 0.6) {
                cellBg = "bg-rose-950/30 text-rose-400 font-mono italic text-[8px]";
              } else if (forecastProb > 0.3) {
                cellBg = "bg-amber-950/20 text-amber-400 font-mono italic text-[8px]";
              } else {
                cellBg = "bg-[#0b0e14]/50 text-slate-700 text-[8px]";
              }
              hoverStatTxt = `Forecast: ${Math.round(forecastProb * 100)}% Danger`;
            }

            rowHtml += `
              <div class="h-6 flex items-center justify-center text-[8.5px] font-mono font-bold rounded cursor-help ${cellBg}" title="${bg.name} @ H-${hr.toFixed(1)}: ${hoverStatTxt}">
                ${probValText || "-"}
              </div>
            `;
          });

          rowHtml += "</div></div>";
          heatmapContainer.innerHTML += rowHtml;
        });
      }

      // ==========================================
      // 4. Figure 4: 4-Panel Site detail plots
      // ==========================================
      const bId = document.getElementById("select-research-barangay").value || "B1";
      const bgInfo = simState.barangays.find(b => b.id === bId);
      
      if (bgInfo) {
        // --- 4A. Simulated Depth Trajectory SVG ---
        const f4aSvg = document.getElementById("fig4a-svg");
        if (f4aSvg) {
          f4aSvg.innerHTML = "";
          const w = 200, h = 100;
          const padL = 20, padB = 15, padT = 10, padR = 10;
          const mapXi = (t) => padL + (t / 6.0) * (w - padL - padR);
          const mapYi = (d) => h - padB - (d / 2.5) * (h - padT - padB);

          let contents = `
            <!-- Gridlines -->
            <line x1="${padL}" y1="${mapYi(1.0)}" x2="${w - padR}" y2="${mapYi(1.0)}" stroke="#111827" stroke-dasharray="2,2" />
            <line x1="${padL}" y1="${mapYi(2.0)}" x2="${w - padR}" y2="${mapYi(2.0)}" stroke="#111827" stroke-dasharray="2,2" />
            <text x="${padL - 3}" y="${mapYi(1.0) + 2}" fill="#475569" font-size="7" text-anchor="end">1m</text>
            <text x="${padL - 3}" y="${mapYi(2.0) + 2}" fill="#475569" font-size="7" text-anchor="end">2m</text>
            <line x1="${padL}" y1="${padT}" x2="${padL}" y2="${h - padB}" stroke="#334155" />
            <line x1="${padL}" y1="${h - padB}" x2="${w - padR}" y2="${h - padB}" stroke="#334155" />
          `;

          if (history.length > 0) {
            // Draw Confidence Band Polygon
            // Let's model the S.D. as roughly +/- 35% around depths
            let topPoints = [];
            let rPoints = [];
            history.forEach(pt => {
              const d = pt.barangayDepths ? (pt.barangayDepths[bId] || 0.0) : 0.0;
              const tX = mapXi(pt.time);
              topPoints.push(`${tX.toFixed(1)},${mapYi(Math.max(0.0, d - 0.35)).toFixed(1)}`);
              rPoints.unshift(`${tX.toFixed(1)},${mapYi(Math.min(2.5, d + 0.35)).toFixed(1)}`);
            });
            const polyPoints = [...topPoints, ...rPoints].join(" ");
            contents += `<polygon points="${polyPoints}" fill="rgba(168, 85, 247, 0.15)" stroke="none" />`;

            // Draw Median Realized Depths
            const medPoints = history.map(pt => {
              const d = pt.barangayDepths ? (pt.barangayDepths[bId] || 0.0) : 0.0;
              return `${mapXi(pt.time).toFixed(1)},${mapYi(d).toFixed(1)}`;
            }).join(" ");
            contents += `<polyline points="${medPoints}" fill="none" stroke="#a855f7" stroke-width="1.8" />`;
          }
          f4aSvg.innerHTML = contents;
        }

        // --- 4B. Population Outcome Histogram SVG ---
        const f4bSvg = document.getElementById("fig4b-svg");
        if (f4bSvg) {
          f4bSvg.innerHTML = "";
          // Compute status totals for agents originating from this Barangay
          const originAgents = simState.agents.filter(a => a.sourceBarangayId === bId) || [];
          const cntSafe = originAgents.filter(a => a.status === "Safe").length;
          const cntPrep = originAgents.filter(a => a.status === "Preparing").length;
          const cntEvac = originAgents.filter(a => a.status === "Evacuating").length;
          const cntStuck = originAgents.filter(a => a.status === "Stuck" || a.status === "RescueNeeded").length;
          const cntCas = originAgents.filter(a => a.status === "Casualty").length;
          const totalCohort = originAgents.length || 1;

          const statuses = [
            { label: "Safe", val: cntSafe, color: "#10b981" },
            { label: "Prep", val: cntPrep, color: "#a855f7" },
            { label: "Evac", val: cntEvac, color: "#eab308" },
            { label: "Stuck", val: cntStuck, color: "#fb923c" },
            { label: "Lost", val: cntCas, color: "#f43f5e" }
          ];

          const w = 200, h = 100;
          const padL = 20, padB = 15, padT = 5, padR = 5;
          let contents = `
            <line x1="${padL}" y1="${padT}" x2="${padL}" y2="${h - padB}" stroke="#1e293b" />
            <line x1="${padL}" y1="${h - padB}" x2="${w - padR}" y2="${h - padB}" stroke="#334155" />
          `;

          const barCount = statuses.length;
          const availW = w - padL - padR;
          const colW = Math.floor(availW / barCount) - 4;

          statuses.forEach((st, i) => {
            const x = padL + i * (availW / barCount) + 3;
            const barH = Math.round((st.val / totalCohort) * (h - padB - padT));
            const y = h - padB - barH;

            // Draw cylinder bar
            contents += `
              <rect x="${x}" y="${y}" width="${colW}" height="${barH}" fill="${st.color}" rx="1.5" />
              <text x="${x + colW / 2}" y="${h - 5}" fill="#64748b" font-size="7" text-anchor="middle">${st.label}</text>
              <text x="${x + colW / 2}" y="${y - 3}" fill="#e2e8f0" font-size="7" font-weight="bold" text-anchor="middle">${st.val}</text>
            `;
          });
          f4bSvg.innerHTML = contents;
        }

        // --- 4C. Drowning Casualty Hazard Curve SVG ---
        const f4cSvg = document.getElementById("fig4c-svg");
        if (f4cSvg) {
          f4cSvg.innerHTML = "";
          const w = 200, h = 80;
          const padL = 20, padB = 15, padT = 10, padR = 10;
          const mapX = (t) => padL + (t / 6.0) * (w - padL - padR);
          const mapY = (p) => h - padB - (p / 100) * (h - padT - padB);

          let contents = `
            <!-- Gridlines -->
            <line x1="${padL}" y1="${mapY(50)}" x2="${w - padR}" y2="${mapY(50)}" stroke="#111827" stroke-dasharray="2,2" />
            <text x="${padL - 3}" y="${mapY(50) + 2}" fill="#475569" font-size="7" text-anchor="end">50%</text>
            <line x1="${padL}" y1="${padT}" x2="${padL}" y2="${h - padB}" stroke="#334155" />
            <line x1="${padL}" y1="${h - padB}" x2="${w - padR}" y2="${h - padB}" stroke="#334155" />
          `;

          // Calculate cumulative drowning probability over time for origins of this Barangay
          const originAgents = simState.agents.filter(a => a.sourceBarangayId === bId) || [];
          const totalO = originAgents.length || 1;

          if (history.length > 0) {
            const curvePoints = history.map(pt => {
              // Extract the ratio of dead units at each time step
              // For visualization, dead ratio calculated based on current run
              let casualtiesAtT = pt.casualtyCount;
              // To make it specific to the actual Barangay, estimate proportional casualty hazard profile
              const ratio = Math.min(100, Math.round((casualtiesAtT / (simState.agents.length || 1)) * 100));
              return `${mapX(pt.time).toFixed(1)},${mapY(ratio).toFixed(1)}`;
            }).join(" ");

            contents += `<polyline points="${curvePoints}" fill="none" stroke="#f43f5e" stroke-width="1.8" />`;
          }
          f4cSvg.innerHTML = contents;
        }

        // --- 4D. Env parameters metrics ---
        const f4dStats = document.getElementById("fig4d-stats");
        if (f4dStats) {
          // Compute local risk coefficient index
          const maxLevel = bgInfo.floodDepth || 0.0;
          let severity = "SAFE LOW RISK";
          let colorClass = "text-emerald-400";
          if (maxLevel > 0.8 || bgInfo.floodProb > 0.75) {
            severity = "CRITICAL / SEVERE";
            colorClass = "text-rose-500 font-extrabold animate-pulse";
          } else if (maxLevel > 0.3 || bgInfo.floodProb > 0.3) {
            severity = "MODERATE ZONE";
            colorClass = "text-amber-500 font-bold";
          }

          f4dStats.innerHTML = `
            <div class="bg-slate-900 border border-slate-950 p-1 rounded-lg flex flex-col justify-center text-center">
              <span class="text-[8px] text-slate-500 uppercase">Basin Zone</span>
              <strong class="text-cyan-400 uppercase text-[9px] font-bold block truncate">${bgInfo.riverSourceProximity}</strong>
            </div>
            <div class="bg-slate-900 border border-slate-950 p-1 rounded-lg flex flex-col justify-center text-center">
              <span class="text-[8px] text-slate-500 uppercase">Base Elevation</span>
              <strong class="text-slate-300 text-[10px] font-extrabold">${bgInfo.elevation} Meters</strong>
            </div>
            <div class="bg-slate-900 border border-slate-950 p-1 rounded-lg flex flex-col justify-center text-center">
              <span class="text-[8px] text-slate-500 uppercase">Live Depth</span>
              <strong class="text-purple-400 text-[10px] font-extrabold">${maxLevel.toFixed(2)} M</strong>
            </div>
            <div class="bg-slate-900 border border-slate-950 p-1 rounded-lg flex flex-col justify-center text-center">
              <span class="text-[8px] text-slate-500 uppercase">Hazard Index</span>
              <strong class="${colorClass} text-[8.5px] truncate block uppercase font-mono">${severity}</strong>
            </div>
          `;
        }
      }
    }

    function updateRescueFleet() {
      if (!simState) return;
      
      const panel = document.getElementById("rescue-fleet-panel");
      panel.innerHTML = "";
      
      simState.rescuers.forEach(resc => {
        let statusText = "Standby / Idle";
        let statusStyle = "bg-slate-900 border border-slate-800 text-slate-400";
        
        if (resc.status === "Dispatched") {
          statusText = "En Route to Casualty";
          statusStyle = "bg-emerald-500/10 border border-emerald-500/35 text-emerald-400 animate-pulse";
        } else if (resc.status === "Returning") {
          statusText = "Returning with Survivors";
          statusStyle = "bg-pink-500/10 border border-pink-500/35 text-pink-400 animate-pulse";
        }
        
        const brgy = simState.barangays.find(b => b.id === resc.barangayId);
        const brgyName = brgy ? brgy.name : "Station";
        
        panel.innerHTML += `
          <div class="p-3 bg-[#0b0e14] border border-slate-800 rounded-xl flex flex-col justify-between space-y-2 select-all hover:border-slate-700/50 transition-all font-sans">
            <div>
              <h5 class="font-bold text-[10.5px] text-purple-200 uppercase tracking-wide truncate">${resc.name}</h5>
              <p class="text-[9px] text-slate-500 mt-0.5">Location: ${brgyName}</p>
              <span class="px-2 py-0.5 rounded text-[8px] font-black uppercase text-center block mt-1.5 ${statusStyle}">
                ${statusText}
              </span>
            </div>
            <div class="border-t border-slate-900 pt-2 flex justify-between items-center text-[9px] text-slate-500 font-mono">
              <span>Saved counts:</span>
              <span class="font-bold text-emerald-450">${(resc.rescuedCount * 250).toLocaleString()} citizens</span>
            </div>
          </div>
        `;
      });
    }

    // Initialize tick state on startup
    fetchState();
    
    // Auto pull metrics
    setInterval(fetchState, 350);
    
  </script>
</body>
</html>
"""

# ==========================================
# 5. SERVER LAUNCHING BOOT STRAP
# ==========================================

def main():
    PORT = 3000
    print("[*] Starting Mindanawa Disaster Informatics Lab server...")
    print(f"[*] Standalone Python applet launching on port {PORT}")
    print("[*] Binding to address 0.0.0.0 for container ingress routing...")
    
    server_address = ("0.0.0.0", PORT)
    httpd = ThreadingHTTPServer(server_address, SimulationHTTPHandler)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Shutting down simulation database server...")
        httpd.server_close()
        sys.exit(0)

if __name__ == "__main__":
    main()
