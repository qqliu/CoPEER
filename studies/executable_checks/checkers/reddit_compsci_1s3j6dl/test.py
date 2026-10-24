"""Energy-based models require continuous latent spaces."""

import json

RECORD_ID = "reddit_compsci_1s3j6dl"
SOURCE_QUOTE = "EBMs require continuous latent spaces"

# The quote supplies no concrete model instances, energy functions, latent
# spaces, or definitions from which such instances could be constructed.
COUNTEREXAMPLE_CANDIDATES = ()

witness = None
for candidate in COUNTEREXAMPLE_CANDIDATES:
    witness = candidate
    break

if witness is None:
    result = {
        "record_id": RECORD_ID,
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No witness: the source quote contains no concrete model instance or latent space.",
        "refutation_explanation": "The quote only repeats the claim and supplies no definition of an energy-based model, no meaning of continuous, and no concrete model to test; therefore no counterexample can be decided without adding absent definitions or data.",
        "search_space": "The exact finite candidate space supplied by the quote: 0 concrete energy-based model instances (the empty set).",
    }
else:
    raise AssertionError("The source-defined candidate space must be empty")

print(json.dumps(result, separators=(",", ":")))
