def load_ref_table(ref_table: str) -> dict:
    with open(f"{ref_table}.json") as f:
        return json.load(f)
