"""On the circle γ of radius r centered at −ρ_k, ln|u| is constantly equal to ln r."""

import json


def main():
    radius = 1
    rho_k = 1
    point_x = -2
    point_y = 0

    center_x = -rho_k
    center_y = 0
    offset_x = point_x - center_x
    offset_y = point_y - center_y

    radius_squared = radius * radius
    distance_from_center_squared = (
        offset_x * offset_x + offset_y * offset_y
    )
    modulus_squared = point_x * point_x + point_y * point_y

    on_stated_circle = distance_from_center_squared == radius_squared
    logarithms_defined = radius > 0 and modulus_squared > 0
    log_arguments_unequal = modulus_squared != radius_squared
    counterexample_verified = (
        on_stated_circle and logarithms_defined and log_arguments_unequal
    )

    verdict = "CONFIRMED" if counterexample_verified else "REFUTED_WITNESS_INVALID"
    notes = (
        "Exact integer recomputation confirms that u=-2 lies on the radius-1 "
        "circle centered at -1, while |u|=2, so injectivity of ln on positive "
        "arguments gives ln|u| != ln r. The refuted statement is substantive, "
        "not plainly a typo."
    )
    result = {
        "record_id": "proofwiki_39745__codex_expansion",
        "verdict": verdict,
        "notes": notes,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
