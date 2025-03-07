"""Engineering notes and history for auto parts."""

# Engineering history for various parts
ENGINEERING_HISTORY = {
    "piston": "Designed by Engineer ID: JD123 in 2023. Initial prototype had overheating issues at high RPM. Resolved by Engineer ID: AM456 with improved cooling channels. Final design approved by Engineer ID: RK789.",
    "variable_valve_timing": "Concept developed by Engineer ID: AM456. Electromagnetic actuation proposed by Engineer ID: JD123 as alternative to hydraulic system. Performance testing conducted by Engineer ID: RK789.",
    "fuel_injector": "Patent filed by Engineer ID: RK789 in 2022. Precision manufacturing process developed by Engineer ID: JD123. Durability testing protocol created by Engineer ID: AM456.",
    "turbocharger": "Designed by Engineer ID: AM456. Bearing system optimized by Engineer ID: RK789. Heat management system developed by Engineer ID: JD123.",
    "connecting_rod": "Material selection by Engineer ID: RK789. Stress analysis performed by Engineer ID: JD123. Manufacturing process optimized by Engineer ID: AM456.",
    "brake_pad": "Compound formulation by Engineer ID: JD123. Wear testing by Engineer ID: AM456. Environmental compliance verified by Engineer ID: RK789."
}

def get_engineering_history(part_name):
    """Get engineering history for a specific part."""
    return ENGINEERING_HISTORY.get(part_name, f"No engineering history available for {part_name}.")
