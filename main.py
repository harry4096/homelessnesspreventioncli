def ask_yes_no(question: str) -> bool:
    while True:
        answer = input(question + " (y/n): ").lower().strip()

        if answer in ["y", "n"]:
            return answer == "y"

        print("Please enter y or n.")


def ask_money(question: str, minimum: float = 0) -> float:
    while True:
        value = input(question).strip()

        try:
            value = float(value)
        except ValueError:
            print("Please enter a valid amount.")
            continue

        if value < minimum:
            print(f"Please enter an amount at least £{minimum}.")
            continue

        return value


def ask_whole_number(question: str, minimum: int = 0) -> int:
    while True:
        value = input(question).strip()

        if not value.isdigit():
            print("Please enter a whole number.")
            continue

        value = int(value)

        if value < minimum:
            print(f"Please enter a number at least {minimum}.")
            continue

        return value


def get_review_message(level: str) -> str:
    if level == "Urgent":
        return (
            "Urgent human review recommended. This household shows multiple "
            "serious financial warning signs and may need immediate support."
        )

    if level == "High":
        return (
            "Human review strongly recommended. This household shows significant "
            "financial pressure and may benefit from early intervention."
        )

    if level == "Moderate":
        return (
            "Human review may be useful. This household shows some financial "
            "warning signs, but the situation may not be urgent."
        )

    return (
        "No immediate human review suggested based on financial factors alone. "
        "Continue monitoring if circumstances change."
    )


def calculate_financial_stress(
    data: dict[str, float | int | bool],
) -> tuple[str, list[str], float, float]:
    score = 0
    reasons: list[str] = []

    income = float(data["monthly_income"])
    rent = float(data["monthly_rent"])
    arrears = float(data["arrears_amount"])

    rent_to_income = rent / income
    arrears_to_income = arrears / income

    if rent_to_income >= 0.5:
        score += 25
        reasons.append(f"Rent is very high relative to income ({rent_to_income:.0%}).")
    elif rent_to_income >= 0.35:
        score += 15
        reasons.append(f"Rent is a large share of income ({rent_to_income:.0%}).")

    months_in_arrears = int(data["months_in_arrears"])

    if months_in_arrears >= 2:
        score += 25
        reasons.append(f"{months_in_arrears} months of rent arrears.")
    elif months_in_arrears == 1:
        score += 10
        reasons.append("1 month of rent arrears.")

    if arrears_to_income >= 1:
        score += 20
        reasons.append("Rent arrears are greater than or equal to one month of income.")
    elif arrears_to_income >= 0.5:
        score += 10
        reasons.append("Rent arrears are at least half of monthly income.")

    if data["income_drop"]:
        score += 15
        reasons.append("Recent income drop.")

    if data["universal_credit_deduction"]:
        score += 10
        reasons.append("Recent Universal Credit deduction.")

    if data["utility_or_council_tax_arrears"]:
        score += 10
        reasons.append("Utility or council tax arrears.")

    if float(data["savings"]) < rent:
        score += 10
        reasons.append("Savings are less than one month of rent.")


    if score >= 75:
        level = "Urgent"
    elif score >= 50:
        level = "High"
    elif score >= 25:
        level = "Moderate"
    else:
        level = "Low"

    return level, reasons, rent_to_income, arrears_to_income


def main() -> None:
    print("\nFinancial Housing Stress Assessment\n")
    print("For money questions, enter numbers only. Example: 1200, not £1200.\n")

    monthly_income = ask_money("Monthly household income after tax: £", minimum=1)
    monthly_rent = ask_money("Monthly rent: £", minimum=0)
    savings = ask_money("Emergency savings available: £", minimum=0)

    in_arrears = ask_yes_no("Is the household currently in rent arrears?")

    months_in_arrears = 0
    arrears_amount = 0.0

    if in_arrears:
        months_in_arrears = ask_whole_number(
            "How many months of rent are unpaid?: ",
            minimum=1,
        )

        arrears_amount = ask_money("How much rent is owed?: £", minimum=1)

    income_drop = ask_yes_no("Has the household had a recent income drop?")

    receives_uc = ask_yes_no("Does the household receive Universal Credit?")

    universal_credit_deduction = False

    if receives_uc:
        universal_credit_deduction = ask_yes_no(
            "Has Universal Credit been deducted in the last 9 months?"
        )

    utility_or_council_tax_arrears = ask_yes_no(
        "Does the household have utility or council tax arrears?"
    )

    data = {
        "monthly_income": monthly_income,
        "monthly_rent": monthly_rent,
        "savings": savings,
        "months_in_arrears": months_in_arrears,
        "arrears_amount": arrears_amount,
        "income_drop": income_drop,
        "universal_credit_deduction": universal_credit_deduction,
        "utility_or_council_tax_arrears": utility_or_council_tax_arrears,
    }

    level, reasons, rent_to_income, arrears_to_income = calculate_financial_stress(data)

    review_message = get_review_message(level)

    print("\n--- Result ---")
    print(f"Financial stress level: {level}")
    print(f"Rent-to-income ratio: {rent_to_income:.1%}")
    print(f"Arrears-to-income ratio: {arrears_to_income:.1%}")
    print(f"Review recommendation: {review_message}")

    print("\nMain reasons:")

    if reasons:
        for reason in reasons:
            print(f"- {reason}")
    else:
        print("- No major financial warning signs detected.")

    print("\nNote:")
    print("This is not a prediction of homelessness.")
    print("It is a financial stress assessment to help prioritise human review.")


if __name__ == "__main__":
    main()
