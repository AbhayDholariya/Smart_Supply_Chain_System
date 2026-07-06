"""
LoadLoop AI / Indian Trucking Route-Leg Dataset Generator
===========================================================
Generates a checkpoint/leg-level synthetic dataset simulating Indian B2B
roadways logistics. Each row = one checkpoint/waypoint along a truck's
journey from origin to destination, capturing:
  - where the vehicle is on the route (distance covered / remaining)
  - conditions at that point (road, weather, traffic)
  - whether a disruption happened there, and its knock-on effect
  - fuel consumed so far, fuel remaining, refuel events
  - revised ETA / cascading delay risk

Vectorized with NumPy for row generation + Pandas groupby-cumsum for
sequential logic (fuel depletion, cumulative delay) so it scales to
millions of rows in seconds.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

RNG = np.random.default_rng(42)

# --------------------------------------------------------------------------
# 1. REFERENCE DATA — Indian cities, states, regions (major logistics hubs)
# --------------------------------------------------------------------------
CITIES = [
    # (city, state, region, lat, lon)
    ("Ahmedabad", "Gujarat", "West", 23.03, 72.58),
    ("Surat", "Gujarat", "West", 21.17, 72.83),
    ("Vadodara", "Gujarat", "West", 22.31, 73.18),
    ("Rajkot", "Gujarat", "West", 22.30, 70.80),
    ("Mumbai", "Maharashtra", "West", 19.08, 72.88),
    ("Pune", "Maharashtra", "West", 18.52, 73.86),
    ("Nagpur", "Maharashtra", "West", 21.15, 79.09),
    ("Nashik", "Maharashtra", "West", 20.00, 73.79),
    ("Delhi", "Delhi", "North", 28.70, 77.10),
    ("Gurugram", "Haryana", "North", 28.46, 77.03),
    ("Jaipur", "Rajasthan", "North", 26.92, 75.79),
    ("Jodhpur", "Rajasthan", "North", 26.29, 73.02),
    ("Chandigarh", "Punjab", "North", 30.73, 76.78),
    ("Ludhiana", "Punjab", "North", 30.90, 75.86),
    ("Lucknow", "Uttar Pradesh", "North", 26.85, 80.95),
    ("Kanpur", "Uttar Pradesh", "North", 26.45, 80.33),
    ("Agra", "Uttar Pradesh", "North", 27.18, 78.01),
    ("Bengaluru", "Karnataka", "South", 12.97, 77.59),
    ("Mysuru", "Karnataka", "South", 12.30, 76.64),
    ("Chennai", "Tamil Nadu", "South", 13.08, 80.27),
    ("Coimbatore", "Tamil Nadu", "South", 11.02, 76.96),
    ("Madurai", "Tamil Nadu", "South", 9.93, 78.12),
    ("Hyderabad", "Telangana", "South", 17.39, 78.49),
    ("Vijayawada", "Andhra Pradesh", "South", 16.51, 80.65),
    ("Kochi", "Kerala", "South", 9.93, 76.27),
    ("Kolkata", "West Bengal", "East", 22.57, 88.36),
    ("Patna", "Bihar", "East", 25.59, 85.14),
    ("Ranchi", "Jharkhand", "East", 23.34, 85.31),
    ("Bhubaneswar", "Odisha", "East", 20.30, 85.82),
    ("Guwahati", "Assam", "East", 26.14, 91.74),
    ("Indore", "Madhya Pradesh", "Central", 22.72, 75.86),
    ("Bhopal", "Madhya Pradesh", "Central", 23.26, 77.41),
    ("Raipur", "Chhattisgarh", "Central", 21.25, 81.63),
]
CITY_NAMES = [c[0] for c in CITIES]
CITY_STATE = {c[0]: c[1] for c in CITIES}
CITY_REGION = {c[0]: c[2] for c in CITIES}
CITY_LAT = {c[0]: c[3] for c in CITIES}
CITY_LON = {c[0]: c[4] for c in CITIES}

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))

VEHICLE_TYPES = {
    # type: (tank_capacity_L, base_mileage_kmpl, max_load_tons)
    "Container Truck (32ft)": (300, 3.4, 25),
    "Trailer (40ft)":         (400, 3.0, 35),
    "LCV (Tata Ace class)":   (60,  9.5, 1.5),
    "Mini Truck (14ft)":      (120, 6.5, 7),
    "Refrigerated Truck":     (300, 2.8, 18),
}
VEHICLE_LIST = list(VEHICLE_TYPES.keys())
VEHICLE_WEIGHTS = [0.30, 0.25, 0.15, 0.20, 0.10]

CARGO_TYPES = ["FMCG", "Electronics", "Pharma", "Textiles & Apparel",
               "Auto Parts", "Perishables/Agri", "Machinery/Industrial",
               "E-commerce Parcels", "Cement/Building Material", "Chemicals"]

CARRIERS = ["BharatFreight Logistics", "TransIndia Carriers", "VLCC Roadways",
            "SwiftHaul Transport", "Rathi Road Lines", "GatiSpeed Cargo",
            "Delhivery Freight", "NationalTrans Movers", "Shree Balaji Transport",
            "Om Sai Roadlines"]

ROUTE_CORRIDORS = ["NH48 (Delhi-Mumbai)", "NH44 (North-South Corridor)",
                    "NH16 (East Coast Road)", "NH27 (East-West Corridor)",
                    "NH19 (Delhi-Kolkata)", "Golden Quadrilateral",
                    "NH8 (Delhi-Jaipur-Ahmedabad)", "NH65 (Pune-Hyderabad)"]

CHECKPOINT_TYPES = ["Toll Plaza", "RTO Check Post", "Weighbridge Station",
                     "Fuel Station", "City Distribution Hub", "State Border Check",
                     "Rest Area / Dhaba Stop", "Highway Patrol Checkpoint"]
CHECKPOINT_WEIGHTS = [0.28, 0.10, 0.08, 0.14, 0.10, 0.10, 0.14, 0.06]

ROAD_TYPES = ["Expressway", "National Highway", "State Highway", "Rural/District Road"]
ROAD_WEIGHTS = [0.15, 0.50, 0.25, 0.10]

ROAD_CONDITIONS = ["Good", "Moderate", "Poor", "Under Construction"]
ROAD_COND_WEIGHTS = [0.45, 0.30, 0.15, 0.10]

WEATHER_CONDITIONS = ["Clear", "Light Rain", "Heavy Rain/Waterlogging", "Fog/Low Visibility",
                       "Heatwave", "Thunderstorm", "Cloudy"]
WEATHER_WEIGHTS = [0.45, 0.15, 0.10, 0.08, 0.10, 0.05, 0.07]

TRAFFIC_CONDITIONS = ["Free Flow", "Moderate", "Heavy", "Jammed"]
TRAFFIC_WEIGHTS = [0.40, 0.30, 0.20, 0.10]

DISRUPTION_TYPES = ["Traffic Jam", "Road Accident (ahead)", "Heavy Rain/Flooding",
                     "Vehicle Breakdown", "Tyre Puncture", "Fog Delay",
                     "Landslide/Road Block", "Strike/Bandh", "RTO/Police Checkpoint Delay",
                     "Road Construction Diversion", "Toll Plaza Congestion",
                     "Loading/Unloading Delay", "Fuel Shortage Nearby",
                     "Driver Mandatory Rest Break", "Local Protest/Road Block"]
DISRUPTION_WEIGHTS = [0.16, 0.06, 0.10, 0.08, 0.09, 0.06, 0.03, 0.04, 0.09,
                       0.08, 0.10, 0.06, 0.02, 0.02, 0.01]

SEVERITY_LEVELS = ["Low", "Medium", "High", "Critical"]
SEVERITY_WEIGHTS = [0.45, 0.32, 0.17, 0.06]
SEVERITY_DURATION_RANGE = {   # hours
    "Low": (0.25, 1.0), "Medium": (1.0, 3.0), "High": (3.0, 8.0), "Critical": (8.0, 26.0)
}

ACTIONS = ["Continue on Route", "Recommend Alternate Route", "Hold at Checkpoint",
           "Emergency Stop / Service Required"]

# --------------------------------------------------------------------------
# 2. CONFIG
# --------------------------------------------------------------------------
TARGET_ROWS = 1_000_000
MIN_LEGS, MAX_LEGS = 3, 15
LEG_DISRUPTION_PROB = 0.13     # per-checkpoint probability (aggregates to a
                                # realistic ~70-75% of trips seeing >=1 disruption)
FUEL_STOP_REFILL_TRIGGER = 0.30  # refill if below 30% tank at a fuel station

def weighted_choice(n, options, weights):
    return RNG.choice(options, size=n, p=np.array(weights) / np.sum(weights))

# --------------------------------------------------------------------------
# 3. TRIP-LEVEL GENERATION
# --------------------------------------------------------------------------
def generate_trips(num_trips):
    origin_idx = RNG.integers(0, len(CITY_NAMES), num_trips)
    dest_idx = RNG.integers(0, len(CITY_NAMES), num_trips)
    same = origin_idx == dest_idx
    while same.any():
        dest_idx[same] = RNG.integers(0, len(CITY_NAMES), same.sum())
        same = origin_idx == dest_idx

    origin_city = np.array(CITY_NAMES)[origin_idx]
    dest_city = np.array(CITY_NAMES)[dest_idx]
    origin_lat = np.array([CITY_LAT[c] for c in origin_city])
    origin_lon = np.array([CITY_LON[c] for c in origin_city])
    dest_lat = np.array([CITY_LAT[c] for c in dest_city])
    dest_lon = np.array([CITY_LON[c] for c in dest_city])

    straight_km = haversine_km(origin_lat, origin_lon, dest_lat, dest_lon)
    road_factor = RNG.uniform(1.15, 1.35, num_trips)   # roads aren't straight lines
    total_distance_km = np.round(straight_km * road_factor, 1)
    total_distance_km = np.clip(total_distance_km, 80, 3000)

    vehicle_type = weighted_choice(num_trips, VEHICLE_LIST, VEHICLE_WEIGHTS)
    tank_cap = np.array([VEHICLE_TYPES[v][0] for v in vehicle_type], dtype=float)
    base_mileage = np.array([VEHICLE_TYPES[v][1] for v in vehicle_type], dtype=float)
    max_load = np.array([VEHICLE_TYPES[v][2] for v in vehicle_type], dtype=float)

    cargo_weight_tons = np.round(RNG.uniform(0.3, 1.0, num_trips) * max_load, 2)
    # heavier relative load -> slightly worse mileage
    load_factor = cargo_weight_tons / max_load
    avg_mileage_kmpl = np.round(base_mileage * (1 - 0.18 * load_factor), 2)

    cargo_type = weighted_choice(num_trips, CARGO_TYPES,
                                  [0.16, 0.10, 0.08, 0.12, 0.10, 0.12, 0.08, 0.14, 0.06, 0.04])
    cargo_value_inr = np.round(cargo_weight_tons * RNG.uniform(15000, 120000, num_trips), 0)

    carrier_company = weighted_choice(num_trips, CARRIERS,
                                       [0.12, 0.11, 0.08, 0.10, 0.09, 0.09, 0.13, 0.10, 0.10, 0.08])
    route_corridor = RNG.choice(ROUTE_CORRIDORS, num_trips)

    driver_id = np.array([f"DRV{n:06d}" for n in RNG.integers(1, 40000, num_trips)])
    driver_experience_years = RNG.integers(1, 25, num_trips)

    vehicle_number_state_code = RNG.choice(
        ["GJ", "MH", "DL", "RJ", "PB", "UP", "KA", "TN", "TS", "WB", "MP"], num_trips)
    vehicle_number = np.array([
        f"{s}{RNG.integers(1,29):02d}{chr(RNG.integers(65,91))}{chr(RNG.integers(65,91))}{RNG.integers(1000,9999)}"
        for s in vehicle_number_state_code
    ])

    start_date = datetime(2024, 1, 1)
    planned_departure = np.array([
        start_date + timedelta(days=int(d), hours=int(h))
        for d, h in zip(RNG.integers(0, 730, num_trips), RNG.integers(0, 24, num_trips))
    ])

    expected_avg_speed_kmph = RNG.uniform(35, 55, num_trips)  # network-level assumption
    eta_original = planned_departure + np.array([
        timedelta(hours=float(t)) for t in (total_distance_km / expected_avg_speed_kmph)
    ])

    num_legs = RNG.integers(MIN_LEGS, MAX_LEGS + 1, num_trips)

    trips = pd.DataFrame({
        "trip_id": [f"TRIP{n:07d}" for n in range(1, num_trips + 1)],
        "origin_city": origin_city, "destination_city": dest_city,
        "origin_state": [CITY_STATE[c] for c in origin_city],
        "destination_state": [CITY_STATE[c] for c in dest_city],
        "region": [CITY_REGION[c] for c in origin_city],
        "route_corridor": route_corridor,
        "vehicle_type": vehicle_type, "vehicle_number": vehicle_number,
        "carrier_company": carrier_company,
        "driver_id": driver_id, "driver_experience_years": driver_experience_years,
        "cargo_type": cargo_type, "cargo_weight_tons": cargo_weight_tons,
        "cargo_value_inr": cargo_value_inr,
        "total_route_distance_km": total_distance_km,
        "fuel_tank_capacity_liters": tank_cap, "avg_mileage_kmpl": avg_mileage_kmpl,
        "planned_departure_datetime": planned_departure,
        "eta_original": eta_original,
        "num_legs": num_legs,
    })
    return trips

# --------------------------------------------------------------------------
# 4. EXPAND TO LEG (CHECKPOINT) LEVEL
# --------------------------------------------------------------------------
def expand_to_legs(trips):
    num_legs = trips["num_legs"].to_numpy()
    total_rows = num_legs.sum()

    leg_seq = np.concatenate([np.arange(1, n + 1) for n in num_legs])
    trip_row_idx = np.repeat(np.arange(len(trips)), num_legs)

    legs = trips.iloc[trip_row_idx].drop(columns=["num_legs"]).reset_index(drop=True)
    legs["leg_sequence_num"] = leg_seq
    legs["leg_id"] = [f"{t}-L{s:02d}" for t, s in zip(legs["trip_id"], leg_seq)]

    legs_total = np.repeat(num_legs, num_legs)
    # progress fraction along the route for this checkpoint, with jitter so
    # segment lengths aren't perfectly uniform
    base_frac = leg_seq / legs_total
    jitter = RNG.uniform(-0.03, 0.03, total_rows)
    frac = np.clip(base_frac + jitter, 0.02, 1.0)
    frac = np.where(leg_seq == legs_total, 1.0, frac)  # last leg = destination

    legs["distance_from_origin_km"] = np.round(frac * legs["total_route_distance_km"], 1)
    legs["distance_remaining_km"] = np.round(
        legs["total_route_distance_km"] - legs["distance_from_origin_km"], 1)

    # segment distance = distance covered since previous checkpoint (per trip)
    legs["segment_distance_km"] = legs.groupby("trip_id")["distance_from_origin_km"].diff()
    legs["segment_distance_km"] = legs["segment_distance_km"].fillna(legs["distance_from_origin_km"])
    legs["segment_distance_km"] = legs["segment_distance_km"].clip(lower=0.5)

    # checkpoint's own state = pick a plausible state along the corridor (approx:
    # alternate between origin state and destination state region-wise)
    legs["checkpoint_state"] = np.where(
        frac < 0.5, legs["origin_state"], legs["destination_state"])

    legs["checkpoint_name"] = [
        f"{s.split()[0]}-CP{n}" for s, n in zip(legs["checkpoint_state"], leg_seq)
    ]

    n = total_rows
    legs["checkpoint_type"] = weighted_choice(n, CHECKPOINT_TYPES, CHECKPOINT_WEIGHTS)
    legs["road_type"] = weighted_choice(n, ROAD_TYPES, ROAD_WEIGHTS)
    legs["road_condition"] = weighted_choice(n, ROAD_CONDITIONS, ROAD_COND_WEIGHTS)
    legs["weather_condition"] = weighted_choice(n, WEATHER_CONDITIONS, WEATHER_WEIGHTS)
    legs["traffic_condition"] = weighted_choice(n, TRAFFIC_CONDITIONS, TRAFFIC_WEIGHTS)

    month = pd.to_datetime(legs["planned_departure_datetime"]).dt.month
    season = np.select(
        [month.isin([12, 1, 2]), month.isin([3, 4, 5]), month.isin([6, 7, 8, 9])],
        ["Winter", "Summer", "Monsoon"], default="Post-Monsoon")
    legs["season"] = season

    # monsoon months -> bump heavy rain/flooding probability by resampling weather
    # for a subset of monsoon rows
    monsoon_mask = (season == "Monsoon") & (RNG.random(n) < 0.35)
    legs.loc[monsoon_mask, "weather_condition"] = "Heavy Rain/Waterlogging"

    legs["temperature_celsius"] = np.where(
        season == "Summer", RNG.uniform(30, 46, n),
        np.where(season == "Winter", RNG.uniform(8, 24, n), RNG.uniform(20, 34, n))
    ).round(1)
    legs["precipitation_mm"] = np.where(
        legs["weather_condition"].isin(["Heavy Rain/Waterlogging", "Thunderstorm"]),
        RNG.uniform(15, 120, n), np.where(legs["weather_condition"] == "Light Rain",
                                           RNG.uniform(1, 15, n), 0)
    ).round(1)

    legs["is_night_travel"] = (RNG.random(n) < 0.30).astype(int)
    legs["driver_hours_since_last_rest"] = np.round(
        RNG.uniform(0.5, 11, n) + legs["leg_sequence_num"] * RNG.uniform(0.2, 0.6, n), 1)

    # ---- speed & timing ----
    speed_base = np.select(
        [legs["road_type"] == "Expressway", legs["road_type"] == "National Highway",
         legs["road_type"] == "State Highway"],
        [70, 50, 38], default=25
    )
    traffic_penalty = np.select(
        [legs["traffic_condition"] == "Free Flow", legs["traffic_condition"] == "Moderate",
         legs["traffic_condition"] == "Heavy"], [0, 8, 18], default=28)
    weather_penalty = np.select(
        [legs["weather_condition"] == "Heavy Rain/Waterlogging",
         legs["weather_condition"] == "Fog/Low Visibility",
         legs["weather_condition"] == "Thunderstorm"], [15, 20, 12], default=0)
    legs["avg_speed_kmph"] = np.clip(speed_base - traffic_penalty - weather_penalty
                                      + RNG.uniform(-4, 4, n), 8, 90).round(1)

    # ---- fuel ----
    legs["fuel_consumed_since_last_checkpoint_liters"] = np.round(
        legs["segment_distance_km"] / legs["avg_mileage_kmpl"], 2)

    is_fuel_stop = (legs["checkpoint_type"] == "Fuel Station").astype(int)
    legs["is_fuel_stop"] = is_fuel_stop
    refuel_group = legs.groupby("trip_id")["is_fuel_stop"].cumsum().to_numpy()
    legs["_refuel_group"] = refuel_group
    cum_since_refuel = legs.groupby(["trip_id", "_refuel_group"])[
        "fuel_consumed_since_last_checkpoint_liters"].cumsum()
    legs["fuel_level_at_checkpoint_liters"] = np.round(
        np.clip(legs["fuel_tank_capacity_liters"] - cum_since_refuel, 2, None), 2)

    low_fuel = (legs["fuel_level_at_checkpoint_liters"] / legs["fuel_tank_capacity_liters"]
                ) < FUEL_STOP_REFILL_TRIGGER
    legs["fuel_refill_liters"] = np.where(
        (legs["is_fuel_stop"] == 1) & low_fuel,
        np.round(legs["fuel_tank_capacity_liters"] - legs["fuel_level_at_checkpoint_liters"]
                  + RNG.uniform(-5, 5, n), 1).clip(0, None), 0.0)
    legs["fuel_price_at_location_inr_per_liter"] = np.round(RNG.uniform(89, 102, n), 2)

    # ---- disruptions ----
    disruption_occurred = (RNG.random(n) < LEG_DISRUPTION_PROB).astype(int)
    legs["disruption_occurred"] = disruption_occurred
    dtype = weighted_choice(n, DISRUPTION_TYPES, DISRUPTION_WEIGHTS)
    legs["disruption_type"] = np.where(disruption_occurred == 1, dtype, "None")

    severity = weighted_choice(n, SEVERITY_LEVELS, SEVERITY_WEIGHTS)
    legs["disruption_severity"] = np.where(disruption_occurred == 1, severity, "None")

    duration = np.zeros(n)
    for lvl, (lo, hi) in SEVERITY_DURATION_RANGE.items():
        mask = (disruption_occurred == 1) & (severity == lvl)
        duration[mask] = RNG.uniform(lo, hi, mask.sum())
    legs["disruption_duration_hours"] = np.round(duration, 2)
    legs["delay_added_hours"] = legs["disruption_duration_hours"]  # 1:1 for this model

    hist_rate_noise = RNG.uniform(0.05, 0.45, n)
    legs["historical_disruption_rate_at_location"] = np.round(hist_rate_noise, 2)

    remaining_frac = legs["distance_remaining_km"] / legs["total_route_distance_km"].replace(0, np.nan)
    remaining_frac = remaining_frac.fillna(0)
    severity_weight = np.select(
        [legs["disruption_severity"] == "Critical", legs["disruption_severity"] == "High",
         legs["disruption_severity"] == "Medium", legs["disruption_severity"] == "Low"],
        [0.9, 0.65, 0.4, 0.15], default=0.0)
    legs["cascading_risk_score"] = np.round(
        np.clip(severity_weight * (0.5 + 0.5 * remaining_frac)
                + 0.2 * legs["historical_disruption_rate_at_location"]
                + RNG.uniform(-0.05, 0.05, n), 0, 1), 3)

    legs["alternate_route_available"] = (RNG.random(n) < 0.55).astype(int)
    action_idx = np.select(
        [legs["disruption_severity"] == "Critical",
         (legs["disruption_severity"] == "High") & (legs["alternate_route_available"] == 1),
         legs["disruption_severity"] == "High",
         legs["disruption_severity"].isin(["Medium", "Low"])],
        [3, 1, 2, 0], default=0)
    legs["recommended_action"] = np.array(ACTIONS)[action_idx]

    legs["gst_checkpost_delay_mins"] = np.where(
        legs["checkpoint_type"] == "State Border Check", RNG.integers(5, 90, n), 0)
    legs["toll_cost_inr"] = np.where(
        legs["checkpoint_type"] == "Toll Plaza", RNG.integers(65, 395, n), 0)

    # ---- cumulative delay & revised ETA (sequential per trip) ----
    legs["cumulative_delay_hours"] = legs.groupby("trip_id")["delay_added_hours"].cumsum()
    legs["eta_revised"] = pd.to_datetime(legs["eta_original"]) + pd.to_timedelta(
        legs["cumulative_delay_hours"], unit="h")

    trip_final_delay = legs.groupby("trip_id")["cumulative_delay_hours"].transform("max")
    legs["final_delivery_status"] = np.select(
        [trip_final_delay < 2, trip_final_delay < 8], ["On-Time", "Delayed"],
        default="Critically Delayed")

    legs["checkpoint_timestamp"] = pd.to_datetime(legs["planned_departure_datetime"]) + \
        pd.to_timedelta(legs["distance_from_origin_km"] / legs["avg_speed_kmph"], unit="h") + \
        pd.to_timedelta(legs["cumulative_delay_hours"], unit="h")

    legs = legs.drop(columns=["is_fuel_stop", "_refuel_group"])
    return legs

# --------------------------------------------------------------------------
# 5. MAIN
# --------------------------------------------------------------------------
def main(target_rows=TARGET_ROWS, out_path="/mnt/user-data/outputs/indian_supply_chain_route_legs.csv"):
    avg_legs = (MIN_LEGS + MAX_LEGS) / 2
    num_trips = int(target_rows / avg_legs * 1.02)  # small buffer, trimmed at the end

    trips = generate_trips(num_trips)
    legs = expand_to_legs(trips)

    if len(legs) > target_rows:
        legs = legs.iloc[:target_rows].reset_index(drop=True)

    col_order = [
        "trip_id", "leg_id", "leg_sequence_num",
        "origin_city", "origin_state", "destination_city", "destination_state",
        "region", "route_corridor",
        "vehicle_type", "vehicle_number", "carrier_company",
        "driver_id", "driver_experience_years",
        "cargo_type", "cargo_weight_tons", "cargo_value_inr",
        "total_route_distance_km", "distance_from_origin_km", "distance_remaining_km",
        "segment_distance_km",
        "checkpoint_name", "checkpoint_type", "checkpoint_state",
        "road_type", "road_condition",
        "weather_condition", "season", "temperature_celsius", "precipitation_mm",
        "traffic_condition", "is_night_travel", "driver_hours_since_last_rest",
        "avg_speed_kmph",
        "fuel_tank_capacity_liters", "avg_mileage_kmpl",
        "fuel_consumed_since_last_checkpoint_liters", "fuel_level_at_checkpoint_liters",
        "fuel_refill_liters", "fuel_price_at_location_inr_per_liter",
        "disruption_occurred", "disruption_type", "disruption_severity",
        "disruption_duration_hours", "delay_added_hours", "cumulative_delay_hours",
        "cascading_risk_score", "alternate_route_available", "recommended_action",
        "historical_disruption_rate_at_location",
        "gst_checkpost_delay_mins", "toll_cost_inr",
        "planned_departure_datetime", "checkpoint_timestamp",
        "eta_original", "eta_revised", "final_delivery_status",
    ]
    legs = legs[col_order]

    legs.to_csv(out_path, index=False)

    print(f"Rows generated : {len(legs):,}")
    print(f"Columns        : {len(legs.columns)}")
    print(f"Unique trips   : {legs['trip_id'].nunique():,}")
    print(f"Disruption rate (per checkpoint): {legs['disruption_occurred'].mean():.2%}")
    trip_level_disruption = legs.groupby('trip_id')['disruption_occurred'].max().mean()
    print(f"Trips with >=1 disruption       : {trip_level_disruption:.2%}")
    print(legs['final_delivery_status'].value_counts(normalize=True).round(3))
    print(f"Saved to: {out_path}")
    return legs

if __name__ == "__main__":
    main()
