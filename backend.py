# backend.py
# Hashing, bill calculation, helpers

import hashlib
import random
import datetime
from typing import Tuple, Union, Dict

def hash_password(password: str) -> str:
    """Return SHA-256 hex digest for password (simple, no extra packages)."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash

def calculate_bill(units: float, customer_type: str) -> Union[Tuple[float,float,float,float], Dict[str, str]]:
    """
    Dynamic slab rates with validation; returns (energy_charge, fixed_charge, gst, total) or error dict
    """
    # Maximum allowed units per month
    max_domestic = 10000
    max_commercial = 50000

    units = float(units) if units else 0.0
    if customer_type.lower() == "domestic":
        if units > max_domestic:
            return {"error": "Unit value exceeds permissible usage range for domestic. Please recheck input."}
        base_rate = 1.5
        fixed = 50.0
    else:
        # commercial
        if units > max_commercial:
            return {"error": "Unit value exceeds permissible usage range for commercial. Please recheck input."}
        base_rate = 3.5
        fixed = 100.0

    energy = 0.0
    remaining_units = units
    slab = 0
    while remaining_units > 0:
        slab += 1
        rate = base_rate + (slab - 1) * 0.5
        slab_units = min(remaining_units, 100)
        energy += slab_units * rate
        remaining_units -= slab_units

    gst = energy * 0.18
    total = energy + fixed + gst
    # Round
    return round(energy,2), round(fixed,2), round(gst,2), round(total,2)

def new_bill_number() -> str:
    return f"BILL{random.randint(10000, 99999)}"

def make_bill(customer_name: str, customer_type: str, units: float, status: str = "Unpaid") -> Union[dict, Dict[str, str]]:
    result = calculate_bill(units, customer_type)
    if isinstance(result, dict) and "error" in result:
        return result
    energy, fixed, gst, total = result
    bill_no = new_bill_number()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "bill_no": bill_no,
        "customer_name": customer_name,
        "customer_type": customer_type,
        "units": units,
        "energy_charge": energy,
        "fixed_charge": fixed,
        "gst": gst,
        "total": total,
        "status": status,
        "created_at": now
    }
