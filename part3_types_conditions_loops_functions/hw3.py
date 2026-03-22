#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"
INCORRECT_CATEGORY_MSG = "Invalid category!"
MONTHS_THIRTY_ONE = (1, 3, 5, 7, 8, 10, 12)
MONTHS_THIRTY = (4, 6, 9, 11)
MONTHS_NUMBER = 12
DAYS_THIRTY_ONE = 31
DAYS_THIRTY = 30
DAYS_TWENTY_NINE = 29
DAYS_TWENTY_EIGHT = 28
FEBRUARY = 2
LEN_THREE = 3
LEN_TWO = 2
LEN_FOUR = 4
AMOUNT_KEY = "amount"
DATE_KEY = "date"
TYPE_KEY = "type"

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": (),
}
CATEGORIES_COMMAND = "categories"

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    if year % 4 == 0 and year % 100 != 0:
        return True
    return year % 400 == 0


def is_valid(day: int, month: int, year: int) -> bool:
    if day < 1 or not (1 <= month <= MONTHS_NUMBER):
        return False

    if (month in MONTHS_THIRTY_ONE and not (1 <= day <= DAYS_THIRTY_ONE)) or (
            month in MONTHS_THIRTY and not (1 <= day <= DAYS_THIRTY)
    ):
        return False

    if month == FEBRUARY:
        if is_leap_year(year):
            return day <= DAYS_TWENTY_NINE
        return day <= DAYS_TWENTY_EIGHT

    return True


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    splitted_date = maybe_dt.split("-")
    if len(splitted_date) != LEN_THREE:
        return None

    day, month, year = map(int, splitted_date)

    if not (is_valid(day, month, year)):
        return None

    return day, month, year


def is_category(category: str) -> bool:
    parts = category.split("::")
    if len(parts) != LEN_TWO:
        return False

    first_part, second_part = parts

    return first_part in EXPENSE_CATEGORIES and second_part in EXPENSE_CATEGORIES[first_part]


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    date = extract_date(income_date)

    if date is None:
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({TYPE_KEY: "income", AMOUNT_KEY: amount, DATE_KEY: date})

    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    categories_available = []
    for category, detailed_cats in EXPENSE_CATEGORIES.items():
        categories_available.extend([f"{category}::{detailed_cat}" for detailed_cat in detailed_cats])
    return "\n".join(categories_available)


def cost_handler(category: str, amount: float, income_date: str) -> str:
    if category == CATEGORIES_COMMAND:
        return cost_categories_handler()

    if not is_category(category):
        return NOT_EXISTS_CATEGORY

    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    date = extract_date(income_date)

    if date is None:
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({TYPE_KEY: "cost", "category": category, AMOUNT_KEY: amount, DATE_KEY: date})

    return OP_SUCCESS_MSG


def is_before(operation_date: tuple[int, int, int],
              date: tuple[int, int, int]) -> bool:
    return operation_date <= date


def is_same_month(operation_date: tuple[int, int, int],
                  date: tuple[int, int, int]) -> bool:
    months_equality = (operation_date[1] == date[1])
    years_equality = (operation_date[2] == date[2])

    return months_equality and years_equality


def monthly_statistics(income: float, expense: float) -> str:
    difference = income - expense
    if difference >= 0:
        return f"This month, the profit amounted to {difference:.2f} rubles."
    return f"This month, the loss amounted to {abs(difference):.2f} rubles."


def stats_handler(date: str) -> str:
    stats_date = extract_date(date)

    if stats_date is None:
        return INCORRECT_DATE_MSG

    income_data = calculate_stats_income(stats_date)
    expense_data = calculate_stats_expense(stats_date)

    return create_answer(date, income_data, expense_data)


def calculate_stats_income(stats_date: tuple[int, int, int]) -> tuple[float, float]:
    total_income: float = 0
    this_month_income: float = 0

    for operation in financial_transactions_storage:
        if operation[TYPE_KEY] == "income":
            if is_before(operation[DATE_KEY], stats_date):
                total_income += operation[AMOUNT_KEY]

            if is_same_month(operation[DATE_KEY], stats_date):
                this_month_income += operation[AMOUNT_KEY]

    return total_income, this_month_income


def calculate_stats_expense(
        stats_date: tuple[int, int, int]
) -> tuple[float, float, dict[str, float]]:
    total_expense: float = 0
    this_month_expense: float = 0
    categories: dict[str, float] = {}

    for operation in financial_transactions_storage:
        if operation[TYPE_KEY] == "cost":
            if is_before(operation[DATE_KEY], stats_date):
                total_expense += operation[AMOUNT_KEY]

            if is_same_month(operation[DATE_KEY], stats_date):
                this_month_expense += operation[AMOUNT_KEY]

                category = operation["category"]
                categories[category] = categories.get(category, 0) + operation[AMOUNT_KEY]

    return total_expense, this_month_expense, categories


def create_answer(date: str, income_data: tuple[float, float],
                  expense_data: tuple[float, float, dict[str, float]]) -> str:
    difference = income_data[0] - expense_data[0]
    this_month_income = income_data[1]
    this_month_expense = expense_data[1]

    basic_answer = [
        f"Your statistics as of {date}:",
        f"Total capital: {difference:.2f} rubles",
        monthly_statistics(this_month_income, this_month_expense),
        f"Income: {this_month_income:.2f} rubles",
        f"Expenses: {this_month_expense:.2f} rubles",
        "",
        "Details (category: amount):",
    ]

    answer_with_categories = category_handler(basic_answer, expense_data[2])

    return "\n".join(answer_with_categories)


def category_handler(answer: list[str], categories: dict[str, float]) -> list[str]:
    sorted_categories = sorted(categories.items())

    if len(sorted_categories) == 0:
        return answer

    for i, (category, category_sum) in enumerate(sorted_categories, 1):
        answer.append(f"{i}. {category}: {category_sum:.2f}")
    return answer


def handle_income_case(cmd_args: list[str]) -> str:
    if len(cmd_args) == LEN_THREE:
        amount_str = cmd_args[1].replace(",", ".")
        return income_handler(float(amount_str), cmd_args[2])
    return UNKNOWN_COMMAND_MSG


def handle_cost_case(cmd_args: list[str]) -> str:
    if len(cmd_args) == LEN_FOUR:
        amount_str = cmd_args[2].replace(",", ".")
        return cost_handler(cmd_args[1], float(amount_str), cmd_args[3])
    if len(cmd_args) == LEN_TWO and cmd_args[1] == CATEGORIES_COMMAND:
        return cost_categories_handler()
    return UNKNOWN_COMMAND_MSG


def handle_stats_case(cmd_args: list[str]) -> str:
    if len(cmd_args) == LEN_TWO:
        return stats_handler(cmd_args[1])
    return UNKNOWN_COMMAND_MSG


def match_case_handler(cmd_args: list[str]) -> str:
    result = UNKNOWN_COMMAND_MSG

    match cmd_args[0]:
        case "income":
            result = handle_income_case(cmd_args)

        case "cost":
            result = handle_cost_case(cmd_args)

        case "stats":
            result = handle_stats_case(cmd_args)
    return result


def main() -> None:
    while True:
        command = input().strip()

        if not command:
            continue

        cmd_args = command.split(" ")

        if cmd_args[0] == "exit":
            break

        print(match_case_handler(cmd_args))


if __name__ == "__main__":
    main()
