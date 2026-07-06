"""
Thin wrapper — generates 100k rows from the Indian routing generator
and saves to data/indian_route_legs.csv
"""
import importlib.util, os, pathlib

os.makedirs("data", exist_ok=True)

spec = importlib.util.spec_from_file_location(
    "gen",
    r"c:\Users\adhol\Smart_Supply_Chain_System\generate_indian_routing_dataset.py",
)
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

legs = gen.main(
    target_rows=100_000,
    out_path=r"c:\Users\adhol\Smart_Supply_Chain_System\data\indian_route_legs.csv",
)
print(f"\nDataset ready  →  {len(legs):,} rows  ×  {len(legs.columns)} columns")
