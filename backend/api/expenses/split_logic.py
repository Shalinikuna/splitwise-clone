from decimal import Decimal, ROUND_HALF_UP


def compute_splits(split_type, total_amount, members_data):
    """
    Compute the exact owed amount for each member.

    members_data: list of dicts with keys:
      - user_id
      - amount  (for UNEQUAL)
      - percentage (for PERCENTAGE)
      - shares (for SHARES)

    Returns list of dicts: [{user_id, amount, share_input}]
    """
    total = Decimal(str(total_amount))
    results = []

    if split_type == "equal":
        count = len(members_data)
        if count == 0:
            raise ValueError("No members to split between.")
        per_person = (total / count).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        for m in members_data:
            results.append({"user_id": m["user_id"], "amount": per_person, "share_input": 1})

    elif split_type == "unequal":
        total_assigned = sum(Decimal(str(m["amount"])) for m in members_data)
        diff = (total - total_assigned).quantize(Decimal("0.01"))
        if abs(diff) > Decimal("0.02"):
            raise ValueError(f"Unequal amounts sum ({total_assigned}) != total ({total})")
        for m in members_data:
            results.append({
                "user_id": m["user_id"],
                "amount": Decimal(str(m["amount"])).quantize(Decimal("0.01")),
                "share_input": Decimal(str(m["amount"])),
            })

    elif split_type == "percentage":
        total_pct = sum(Decimal(str(m["percentage"])) for m in members_data)
        if abs(total_pct - Decimal("100")) > Decimal("0.01"):
            raise ValueError(f"Percentages sum to {total_pct}, must be 100.")
        for m in members_data:
            pct = Decimal(str(m["percentage"]))
            amt = (total * pct / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            results.append({"user_id": m["user_id"], "amount": amt, "share_input": pct})

    elif split_type == "shares":
        total_shares = sum(Decimal(str(m["shares"])) for m in members_data)
        if total_shares == 0:
            raise ValueError("Total shares cannot be zero.")
        for m in members_data:
            s = Decimal(str(m["shares"]))
            amt = (total * s / total_shares).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            results.append({"user_id": m["user_id"], "amount": amt, "share_input": s})

    else:
        raise ValueError(f"Unknown split type: {split_type}")

    return results
