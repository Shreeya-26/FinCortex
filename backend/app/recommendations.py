"""Plain, rule-based advice that sits next to the ML score. Easy to read and easy to test."""
from .schemas import CategoryLine, FinancialInput, Platform, PlanStep, Rule503020

PLATFORMS = [
    ("Your bank savings account / RD", "https://www.rbi.org.in/", "Parking 1-3 months of expenses with instant access.", ["Low", "Medium", "High"], "emergency"),
    ("Groww (liquid funds, SIPs)", "https://groww.in/", "Beginner-friendly liquid funds and index-fund SIPs.", ["Low", "Medium", "High"], "invest"),
    ("Zerodha Coin", "https://coin.zerodha.com/", "Direct mutual-fund SIPs with low expense ratios.", ["Low", "Medium", "High"], "invest"),
    ("Bank / post-office FD", "https://www.indiapost.gov.in/", "Capital protection for goals under about 3 years.", ["Low", "Medium"], "invest"),
    ("PPF", "https://www.indiapost.gov.in/", "Long-term, tax-efficient debt for conservative savers.", ["Low", "Medium"], "invest"),
    ("Zerodha Kite", "https://zerodha.com/", "Low-cost brokerage for stocks, ETFs and gold bonds.", ["Medium", "High"], "invest"),
    ("National Pension System", "https://enps.nsdl.com/", "Retirement saving with tax benefits. Not for emergencies.", ["Low", "Medium", "High"], "invest"),
]

ALLOCATION = {
    "Low": {"Mutual Funds": 20, "FD": 40, "Emergency Fund": 30, "Skill Development": 10},
    "Medium": {"Mutual Funds": 40, "FD": 20, "Emergency Fund": 20, "Skill Development": 20},
    "High": {"Mutual Funds": 60, "FD": 10, "Emergency Fund": 15, "Skill Development": 15},
}


def pct(part: float, whole: float) -> float:
    return round(100 * part / whole, 1) if whole else 0.0


def total_expenses(d: FinancialInput) -> float:
    return d.rent + d.food + d.transport + d.emi + d.other_expenses


def breakdown(d: FinancialInput) -> list[CategoryLine]:
    lines = {"Rent": d.rent, "Food": d.food, "Transport": d.transport, "EMI": d.emi, "Other": d.other_expenses}
    return [CategoryLine(category=k, amount=v, pct_of_salary=pct(v, d.salary)) for k, v in lines.items()]


def rule_50_30_20(d: FinancialInput) -> Rule503020:
    needs = d.rent + d.food + d.transport + d.emi
    savings = max(d.salary - total_expenses(d), 0)
    return Rule503020(needs_pct=pct(needs, d.salary), wants_pct=pct(d.other_expenses, d.salary), savings_pct=pct(savings, d.salary))


def warnings_for(d: FinancialInput, emergency_short: bool, high_emi: bool) -> list[str]:
    leftover = d.salary - total_expenses(d)
    out = []
    if high_emi:
        out.append("EMIs take more than 40% of your salary. Avoid taking on new debt.")
    if leftover < 0:
        out.append("You are spending more than you earn. Investing should wait.")
    elif leftover < 0.10 * d.salary:
        out.append("You save less than 10% of your salary. Try trimming discretionary spending.")
    if emergency_short:
        out.append("Your emergency fund is below a 3-month expense buffer.")
    return out


def allocation_for(risk: str, emergency_short: bool, high_emi: bool) -> dict[str, int]:
    alloc = dict(ALLOCATION[risk])
    if emergency_short:                      # move 15 points from mutual funds into the emergency fund
        take = min(15, alloc["Mutual Funds"])
        alloc["Mutual Funds"] -= take
        alloc["Emergency Fund"] += take
    if high_emi:                             # move 10 points from mutual funds into safer FDs
        take = min(10, alloc["Mutual Funds"])
        alloc["Mutual Funds"] -= take
        alloc["FD"] += take
    return alloc


def plan_for(d: FinancialInput, emergency_short: bool, high_emi: bool) -> list[PlanStep]:
    leftover = d.salary - total_expenses(d)
    titles = []
    if emergency_short:
        titles.append(("Build a 3-month emergency buffer first", "Keep new savings in a savings account or liquid fund until your savings cover about three months of expenses."))
    if high_emi:
        titles.append(("Stabilise debt before adding risk", "Consider prepaying part of your highest-rate loan before starting a large SIP."))
    if leftover <= 0:
        titles.append(("Create some leftover before investing", "Cut other spending until at least 10-20% of your salary is free."))
    else:
        titles.append(("Automate the monthly surplus", f"About Rs {round(leftover, -2):,.0f} is free each month. Split it using the suggested allocation."))
        titles.append(("Match products to your horizon", "Under 3 years: FD or liquid funds. 3 to 7 years: hybrid funds. Longer: index funds."))
    return [PlanStep(step=i + 1, title=t, detail=x) for i, (t, x) in enumerate(titles)]


def platforms_for(risk: str, limit: int = 5) -> list[Platform]:
    chosen = [p for p in PLATFORMS if risk in p[3]]
    chosen.sort(key=lambda p: p[4] != "emergency")   # emergency options first
    return [Platform(name=n, url=u, best_for=b) for n, u, b, _, _ in chosen[:limit]]
