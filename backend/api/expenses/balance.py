from decimal import Decimal
from collections import defaultdict
from django.contrib.auth import get_user_model

from .models import Expense, ExpenseSplit
from api.settlements.models import Settlement

User = get_user_model()


def compute_group_balances(group):
    """
    Returns a dict: { user_id: net_balance }
    Positive = is owed money. Negative = owes money.
    """
    balances = defaultdict(Decimal)

    for expense in Expense.objects.filter(group=group).select_related("paid_by").prefetch_related("splits"):
        # Payer gets credit for full amount
        balances[str(expense.paid_by_id)] += expense.amount
        # Each split member gets debited their share
        for split in expense.splits.all():
            balances[str(split.user_id)] -= split.amount

    for settlement in Settlement.objects.filter(group=group):
        # Person who paid gets credit
        balances[str(settlement.paid_by_id)] += settlement.amount
        # Person who received gets debited
        balances[str(settlement.paid_to_id)] -= settlement.amount

    return dict(balances)


def compute_group_balance_matrix(group):
    """
    Returns list of {from_user, to_user, amount} for who owes whom.
    Simple pair-wise — no simplification.
    """
    members = list(group.members.select_related("user").values_list("user_id", flat=True))
    member_set = set(str(m) for m in members)
    owed = defaultdict(lambda: defaultdict(Decimal))  # owed[debtor][creditor]

    for expense in Expense.objects.filter(group=group).select_related("paid_by").prefetch_related("splits"):
        payer_id = str(expense.paid_by_id)
        for split in expense.splits.all():
            debtor_id = str(split.user_id)
            if debtor_id == payer_id:
                continue  # payer doesn't owe themselves
            owed[debtor_id][payer_id] += split.amount

    for settlement in Settlement.objects.filter(group=group):
        paid_by_id = str(settlement.paid_by_id)
        paid_to_id = str(settlement.paid_to_id)
        owed[paid_by_id][paid_to_id] -= settlement.amount
        if owed[paid_by_id][paid_to_id] < 0:
            owed[paid_by_id][paid_to_id] = Decimal("0")

    results = []
    seen_users = set()
    user_cache = {}

    def get_user(uid):
        if uid not in user_cache:
            try:
                user_cache[uid] = User.objects.get(id=uid)
            except User.DoesNotExist:
                user_cache[uid] = None
        return user_cache[uid]

    for debtor_id, creditors in owed.items():
        for creditor_id, amount in creditors.items():
            if amount > Decimal("0.01"):
                debtor = get_user(debtor_id)
                creditor = get_user(creditor_id)
                if debtor and creditor:
                    results.append({
                        "from_user": {"id": debtor_id, "name": debtor.name, "email": debtor.email},
                        "to_user": {"id": creditor_id, "name": creditor.name, "email": creditor.email},
                        "amount": float(amount),
                    })

    return results


def compute_overall_balance(user):
    """
    Returns list of {other_user, amount, direction} across ALL groups.
    direction = 'owe' or 'owed'
    """
    from api.groups.models import GroupMember
    group_ids = GroupMember.objects.filter(user=user).values_list("group_id", flat=True)

    net = defaultdict(Decimal)  # positive means other_user owes me

    for expense in Expense.objects.filter(group_id__in=group_ids).select_related("paid_by").prefetch_related("splits"):
        payer_id = str(expense.paid_by_id)
        user_id = str(user.id)
        for split in expense.splits.all():
            debtor_id = str(split.user_id)
            if payer_id == user_id and debtor_id != user_id:
                net[debtor_id] += split.amount
            elif debtor_id == user_id and payer_id != user_id:
                net[payer_id] -= split.amount

    for settlement in Settlement.objects.filter(group_id__in=group_ids):
        paid_by_id = str(settlement.paid_by_id)
        paid_to_id = str(settlement.paid_to_id)
        user_id = str(user.id)
        if paid_by_id == user_id:
            net[paid_to_id] -= settlement.amount
        elif paid_to_id == user_id:
            net[paid_by_id] += settlement.amount

    results = []
    user_cache = {}
    for other_id, amount in net.items():
        if abs(amount) < Decimal("0.01"):
            continue
        try:
            other = User.objects.get(id=other_id)
        except User.DoesNotExist:
            continue
        results.append({
            "user": {"id": other_id, "name": other.name, "email": other.email},
            "amount": float(abs(amount)),
            "direction": "owed" if amount > 0 else "owe",
        })

    return results
