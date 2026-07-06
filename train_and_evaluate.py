"""
Smart Supply Chain — ML Training & Evaluation
==============================================
Three classification targets trained and evaluated independently:

  Target 1 → disruption_occurred       (Binary: 0 / 1)
  Target 2 → disruption_severity       (Multi-class: Low/Medium/High/Critical)
              trained only on rows where a disruption happened
  Target 3 → final_delivery_status     (Multi-class: On-Time/Delayed/Critically Delayed)
              one row per trip (trip-level aggregation)

Four models per target:
  • Logistic Regression (baseline)
  • Decision Tree
  • Random Forest
  • Gradient Boosting

Metrics: Accuracy · Precision · Recall · F1 (weighted)
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from pathlib import Path
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix,
)

SEP  = "=" * 72
SEP2 = "-" * 72

def banner(txt):  print(f"\n{SEP}\n  {txt}\n{SEP}")
def sub(txt):     print(f"\n{SEP2}\n  {txt}\n{SEP2}")

# Get project root directory (works across machines)
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
MODEL_DIR = PROJECT_ROOT / "backend" / "ml_models"

# Create model directory if it doesn't exist
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# ─── 1. LOAD ──────────────────────────────────────────────────────────────────
DATA = DATA_DIR / "indian_route_legs.csv"

banner("1. Loading Dataset")
df = pd.read_csv(DATA, low_memory=False)
print(f"  Rows      : {len(df):,}")
print(f"  Columns   : {df.shape[1]}")

# ─── 2. DATETIME → NUMERIC ────────────────────────────────────────────────────
for col in ["planned_departure_datetime","checkpoint_timestamp","eta_original","eta_revised"]:
    df[col] = pd.to_datetime(df[col], errors="coerce")

df["departure_hour"]      = df["planned_departure_datetime"].dt.hour
df["departure_dow"]       = df["planned_departure_datetime"].dt.dayofweek
df["departure_month"]     = df["planned_departure_datetime"].dt.month
df["eta_delay_hours"]     = ((df["eta_revised"] - df["eta_original"])
                              .dt.total_seconds() / 3600).fillna(0).clip(0, 100)
df["fuel_pct"]            = (df["fuel_level_at_checkpoint_liters"]
                              / df["fuel_tank_capacity_liters"]).clip(0, 1)
df["route_progress"]      = (df["distance_from_origin_km"]
                              / df["total_route_distance_km"].replace(0, np.nan)
                              ).fillna(0).clip(0, 1)

# ─── 3. FEATURE LISTS ─────────────────────────────────────────────────────────
NUM = [
    "leg_sequence_num",
    "total_route_distance_km","distance_from_origin_km","distance_remaining_km",
    "segment_distance_km",
    "driver_experience_years",
    "cargo_weight_tons",
    "avg_speed_kmph",
    "fuel_tank_capacity_liters","avg_mileage_kmpl",
    "fuel_consumed_since_last_checkpoint_liters","fuel_level_at_checkpoint_liters",
    "fuel_refill_liters",
    "temperature_celsius","precipitation_mm",
    "is_night_travel","driver_hours_since_last_rest",
    "cascading_risk_score","alternate_route_available",
    "historical_disruption_rate_at_location",
    "gst_checkpost_delay_mins","toll_cost_inr",
    "delay_added_hours","cumulative_delay_hours",
    "departure_hour","departure_dow","departure_month",
    "eta_delay_hours","fuel_pct","route_progress",
]
CAT = [
    "origin_city","destination_city","region","route_corridor",
    "vehicle_type","carrier_company","cargo_type",
    "checkpoint_type","road_type","road_condition",
    "weather_condition","traffic_condition","season",
]

NUM = [c for c in NUM if c in df.columns]
CAT = [c for c in CAT if c in df.columns]
ALL_FEAT = NUM + CAT

banner("2. Feature Engineering Summary")
print(f"  Numeric features     : {len(NUM)}")
print(f"  Categorical features : {len(CAT)}")
print(f"  Total features       : {len(ALL_FEAT)}")

# ─── 4. PREPROCESSOR ─────────────────────────────────────────────────────────
prep = ColumnTransformer([
    ("num", StandardScaler(), NUM),
    ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CAT),
], remainder="drop")

# ─── 5. MODELS ────────────────────────────────────────────────────────────────
MODELS = {
    "Logistic Regression": LogisticRegression(max_iter=500, n_jobs=-1, random_state=42),
    "Decision Tree":       DecisionTreeClassifier(max_depth=12, random_state=42),
    "Random Forest":       RandomForestClassifier(n_estimators=150, n_jobs=-1,
                                                   max_depth=15, random_state=42),
    "Gradient Boosting":   GradientBoostingClassifier(n_estimators=150, max_depth=5,
                                                       learning_rate=0.1, random_state=42),
}

results = []

def evaluate(target_name, X, y_raw, note=""):
    banner(f"TARGET → {target_name}  {note}")

    le = LabelEncoder()
    y  = le.fit_transform(y_raw)
    classes = np.array([str(c) for c in le.classes_])

    print(f"  Classes   : {list(classes)}")
    print(f"  Samples   : {len(y):,}")
    vc = pd.Series(y_raw).value_counts()
    print("  Distribution:\n" + vc.to_string())

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.20, random_state=42,
        stratify=y if len(np.unique(y)) > 1 else None,
    )
    print(f"  Train={len(X_tr):,}  Test={len(X_te):,}")

    for name, model in MODELS.items():
        sub(f"{name}  ←  {target_name}")
        pipe = Pipeline([("prep", prep), ("model", model)])
        pipe.fit(X_tr, y_tr)
        yp = pipe.predict(X_te)

        acc  = accuracy_score(y_te, yp)
        prec = precision_score(y_te, yp, average="weighted", zero_division=0)
        rec  = recall_score(y_te, yp, average="weighted", zero_division=0)
        f1   = f1_score(y_te, yp, average="weighted", zero_division=0)

        print(f"\n  Accuracy   : {acc:.4f}  ({acc*100:.2f}%)")
        print(f"  Precision  : {prec:.4f}")
        print(f"  Recall     : {rec:.4f}")
        print(f"  F1-Score   : {f1:.4f}")
        print("\n  Classification Report:")
        print(classification_report(y_te, yp, target_names=classes, zero_division=0))
        print("  Confusion Matrix:")
        cm = pd.DataFrame(confusion_matrix(y_te, yp), index=classes, columns=classes)
        print(cm.to_string())

        results.append({
            "Target": target_name, "Model": name,
            "Accuracy": round(acc, 4), "Precision": round(prec, 4),
            "Recall": round(rec, 4), "F1": round(f1, 4),
        })

# ─── 6. TARGET 1: DISRUPTION PREDICTION (binary) ─────────────────────────────
# Use all rows; no NaN issue because disruption_occurred is always 0 or 1
df_t1 = df[ALL_FEAT + ["disruption_occurred"]].dropna(subset=NUM)
X1 = df_t1[ALL_FEAT]
y1 = df_t1["disruption_occurred"].astype(int)
evaluate("disruption_occurred", X1, y1,
         note="| Binary: will a disruption happen at this checkpoint?")

# ─── 7. TARGET 2: DISRUPTION SEVERITY (multi-class) ──────────────────────────
# Only rows where disruption actually occurred (severity ≠ "None")
sev_map = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}
df_t2 = df[df["disruption_occurred"] == 1].copy()
df_t2 = df_t2[df_t2["disruption_severity"].isin(sev_map.keys())]
df_t2 = df_t2[ALL_FEAT + ["disruption_severity"]].dropna(subset=NUM)
X2 = df_t2[ALL_FEAT]
y2 = df_t2["disruption_severity"]
evaluate("disruption_severity", X2, y2,
         note="| Multi-class: how severe is the disruption?")

# ─── 8. TARGET 3: DELIVERY STATUS (trip-level) ────────────────────────────────
# Aggregate to trip level: use last checkpoint per trip (final state)
df_t3 = (df.sort_values(["trip_id", "leg_sequence_num"])
           .groupby("trip_id", as_index=False)
           .last())

# Trip-level numeric features (means / sums make more sense at trip level)
NUM_T3 = [
    "total_route_distance_km","driver_experience_years","cargo_weight_tons",
    "avg_speed_kmph","fuel_tank_capacity_liters","avg_mileage_kmpl",
    "temperature_celsius","precipitation_mm","is_night_travel",
    "cascading_risk_score","historical_disruption_rate_at_location",
    "cumulative_delay_hours","eta_delay_hours","fuel_pct","route_progress",
    "departure_hour","departure_dow","departure_month",
]
CAT_T3 = [
    "origin_city","destination_city","region","route_corridor",
    "vehicle_type","carrier_company","cargo_type",
    "road_condition","weather_condition","traffic_condition","season",
]
NUM_T3 = [c for c in NUM_T3 if c in df_t3.columns]
CAT_T3 = [c for c in CAT_T3 if c in df_t3.columns]
FEAT_T3 = NUM_T3 + CAT_T3

prep_t3 = ColumnTransformer([
    ("num", StandardScaler(), NUM_T3),
    ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CAT_T3),
], remainder="drop")

MODELS_T3 = {
    "Logistic Regression": LogisticRegression(max_iter=500, n_jobs=-1, random_state=42),
    "Decision Tree":       DecisionTreeClassifier(max_depth=12, random_state=42),
    "Random Forest":       RandomForestClassifier(n_estimators=150, n_jobs=-1,
                                                   max_depth=15, random_state=42),
    "Gradient Boosting":   GradientBoostingClassifier(n_estimators=150, max_depth=5,
                                                       learning_rate=0.1, random_state=42),
}

df_t3c = df_t3[FEAT_T3 + ["final_delivery_status"]].dropna(subset=NUM_T3)
X3 = df_t3c[FEAT_T3]
y3_raw = df_t3c["final_delivery_status"]

banner("TARGET → final_delivery_status  | Multi-class: trip outcome prediction")
le3 = LabelEncoder()
y3  = le3.fit_transform(y3_raw)
classes3 = le3.classes_
print(f"  Classes   : {list(classes3)}")
print(f"  Samples   : {len(y3):,}")
print("  Distribution:\n" + y3_raw.value_counts().to_string())

X3_tr, X3_te, y3_tr, y3_te = train_test_split(
    X3, y3, test_size=0.20, random_state=42, stratify=y3)
print(f"  Train={len(X3_tr):,}  Test={len(X3_te):,}")

for name, model in MODELS_T3.items():
    sub(f"{name}  ←  final_delivery_status")
    pipe = Pipeline([("prep", prep_t3), ("model", model)])
    pipe.fit(X3_tr, y3_tr)
    yp = pipe.predict(X3_te)

    acc  = accuracy_score(y3_te, yp)
    prec = precision_score(y3_te, yp, average="weighted", zero_division=0)
    rec  = recall_score(y3_te, yp, average="weighted", zero_division=0)
    f1   = f1_score(y3_te, yp, average="weighted", zero_division=0)

    print(f"\n  Accuracy   : {acc:.4f}  ({acc*100:.2f}%)")
    print(f"  Precision  : {prec:.4f}")
    print(f"  Recall     : {rec:.4f}")
    print(f"  F1-Score   : {f1:.4f}")
    print("\n  Classification Report:")
    print(classification_report(y3_te, yp, target_names=classes3, zero_division=0))
    print("  Confusion Matrix:")
    cm = pd.DataFrame(confusion_matrix(y3_te, yp), index=classes3, columns=classes3)
    print(cm.to_string())

    results.append({
        "Target": "final_delivery_status", "Model": name,
        "Accuracy": round(acc, 4), "Precision": round(prec, 4),
        "Recall": round(rec, 4), "F1": round(f1, 4),
    })

# ─── 9. TRAIN & SAVE BEST MODELS ──────────────────────────────────────────────
def save_best_model(target_name, X, y_raw, best_model_name, prep, note=""):
    banner(f"SAVING BEST MODEL → {target_name}")
    
    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    
    # Retrain on full dataset
    if target_name == "final_delivery_status":
        pipe = Pipeline([("prep", prep_t3), ("model", MODELS_T3[best_model_name])])
    else:
        pipe = Pipeline([("prep", prep), ("model", MODELS[best_model_name])])
    pipe.fit(X, y)
    
    # Save model and label encoder
    model_path = MODEL_DIR / f"{target_name}_model.joblib"
    le_path = MODEL_DIR / f"{target_name}_label_encoder.joblib"
    joblib.dump(pipe, model_path)
    joblib.dump(le, le_path)
    print(f"  ✅ Model saved → {model_path}")
    print(f"  ✅ Label encoder saved → {le_path}")

banner("SUMMARY — All Models × All Targets")
summary = pd.DataFrame(results)
for tgt, grp in summary.groupby("Target", sort=False):
    grp_sorted = grp.sort_values("Accuracy", ascending=False)
    print(f"\n  ┌─ {tgt}")
    print(grp_sorted[["Model","Accuracy","Precision","Recall","F1"]].to_string(index=False))

banner("BEST MODEL PER TARGET")
best = summary.loc[summary.groupby("Target")["Accuracy"].idxmax()]
print(best[["Target","Model","Accuracy","Precision","Recall","F1"]].to_string(index=False))

# Save best models
best_disruption_occurred = best[best["Target"] == "disruption_occurred"]["Model"].iloc[0]
save_best_model("disruption_occurred", X1, y1, best_disruption_occurred, prep)

best_disruption_severity = best[best["Target"] == "disruption_severity"]["Model"].iloc[0]
save_best_model("disruption_severity", X2, y2, best_disruption_severity, prep)

best_final_delivery_status = best[best["Target"] == "final_delivery_status"]["Model"].iloc[0]
save_best_model("final_delivery_status", X3, y3_raw, best_final_delivery_status, prep_t3)

OUT = DATA_DIR / "model_results.csv"
summary.to_csv(OUT, index=False)
print(f"\n  ✅ Results saved → {OUT}")
banner("DONE ✓")
