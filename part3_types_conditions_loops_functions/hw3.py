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
AVAILABLE_SYMBOLS = "0123456789."

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("SomeCategory", "SomeOtherCategory"),
}
CATEGORIES_COMMAND = "categories"

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    if year % 4 == 0 and year % 100 != 0:
        return True
    return year % 400 == 0


def _is_valid(day: int, month: int, year: int) -> bool:
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

    if not (_is_valid(day, month, year)):
        return None

    return day, month, year


def _parse_amount(amount: str) -> float | None:
    new_amount = amount.strip().replace(",", ".")

    if not new_amount:
        return None

    if new_amount.count(".") > 1:
        return None

    amount_parts = new_amount.split(".")
    if any(part == "" for part in amount_parts):
        return None

    abs_amount = new_amount
    if new_amount[0] in "-+":
        abs_amount = new_amount[1:]

    for symbol in abs_amount:
        if symbol not in AVAILABLE_SYMBOLS:
            return None

    return float(new_amount)


def _is_category(category: str) -> bool:
    parts = category.split("::")
    if len(parts) != LEN_TWO:
        return False

    first_part, second_part = parts

    return first_part in EXPENSE_CATEGORIES and second_part in EXPENSE_CATEGORIES[first_part]


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    date = extract_date(income_date)

    if date is None:
        financial_transactions_storage.append({})
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

    if not _is_category(category):
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY

    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    date = extract_date(income_date)

    if date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({TYPE_KEY: "cost", "category": category, AMOUNT_KEY: amount, DATE_KEY: date})

    return OP_SUCCESS_MSG


def _is_before(op_date: tuple[int, int, int],
               date: tuple[int, int, int]) -> bool:
    op_date_reversed = (op_date[2], op_date[1], op_date[0])
    date_reversed = (date[2], date[1], date[0])

    return op_date_reversed <= date_reversed


def _is_same_month(operation_date: tuple[int, int, int],
                   date: tuple[int, int, int]) -> bool:
    months_equality = (operation_date[1] == date[1])
    years_equality = (operation_date[2] == date[2])

    return months_equality and years_equality


def _monthly_statistics(income: float, expense: float) -> str:
    difference = income - expense
    if difference >= 0:
        return f"This month, the profit amounted to {difference:.2f} rubles."
    return f"This month, the loss amounted to {abs(difference):.2f} rubles."


def stats_handler(date: str) -> str:
    stats_date = extract_date(date)

    if stats_date is None:
        return INCORRECT_DATE_MSG

    income_data = _calculate_stats_income(stats_date)
    expense_data = _calculate_stats_expense(stats_date)

    return _create_statistics(date, income_data, expense_data)


def _calculate_stats_income(stats_date: tuple[int, int, int]) -> tuple[float, float]:
    total_income: float = 0
    this_month_income: float = 0

    for operation in financial_transactions_storage:
        if operation[TYPE_KEY] == "income":
            if _is_before(operation[DATE_KEY], stats_date):
                total_income += operation[AMOUNT_KEY]

            if _is_same_month(operation[DATE_KEY], stats_date):
                this_month_income += operation[AMOUNT_KEY]

    return total_income, this_month_income


def _calculate_stats_expense(
        stats_date: tuple[int, int, int]
) -> tuple[float, float, dict[str, float]]:
    total_expense: float = 0
    this_month_expense: float = 0
    categories: dict[str, float] = {}

    for operation in financial_transactions_storage:
        if operation[TYPE_KEY] == "cost":
            if _is_before(operation[DATE_KEY], stats_date):
                total_expense += operation[AMOUNT_KEY]

            if _is_same_month(operation[DATE_KEY], stats_date):
                this_month_expense += operation[AMOUNT_KEY]

                category = operation["category"]
                categories[category] = categories.get(category, 0) + operation[AMOUNT_KEY]

    return total_expense, this_month_expense, categories


def _create_statistics(date: str, income_data: tuple[float, float],
                       expense_data: tuple[float, float, dict[str, float]]) -> str:
    difference = income_data[0] - expense_data[0]
    this_month_income = income_data[1]
    this_month_expense = expense_data[1]

    basic_answer = [
        f"Your statistics as of {date}:",
        f"Total capital: {difference:.2f} rubles",
        _monthly_statistics(this_month_income, this_month_expense),
        f"Income: {this_month_income:.2f} rubles",
        f"Expenses: {this_month_expense:.2f} rubles",
        "",
        "Details (category: amount):",
    ]

    answer_with_categories = _category_stats_handler(basic_answer, expense_data[2])

    return "\n".join(answer_with_categories)


def _category_stats_handler(answer: list[str], categories: dict[str, float]) -> list[str]:
    sorted_categories = sorted(categories.items())

    if len(sorted_categories) == 0:
        return answer

    for i, (category, category_sum) in enumerate(sorted_categories, 1):
        answer.append(f"{i}. {category}: {_format_category_sum(category_sum)}")
    return answer


def _format_category_sum(category_sum: float) -> str:
    if category_sum.is_integer():
        return f"{int(category_sum)}"
    return f"{category_sum:.2f}"


def _handle_income_case(cmd_args: list[str]) -> str:
    if len(cmd_args) == LEN_THREE:
        parsed_amount = _parse_amount(cmd_args[1])

        if parsed_amount is None:
            return UNKNOWN_COMMAND_MSG

        if parsed_amount <= 0:
            return NONPOSITIVE_VALUE_MSG

        return income_handler(parsed_amount, cmd_args[2])
    return UNKNOWN_COMMAND_MSG


def _handle_cost_case(cmd_args: list[str]) -> str:
    if len(cmd_args) == LEN_FOUR:
        parsed_amount = _parse_amount(cmd_args[2])

        if parsed_amount is None:
            return UNKNOWN_COMMAND_MSG

        if parsed_amount <= 0:
            return NONPOSITIVE_VALUE_MSG

        return cost_handler(cmd_args[1], parsed_amount, cmd_args[3])

    if len(cmd_args) == LEN_TWO and cmd_args[1] == CATEGORIES_COMMAND:
        return cost_categories_handler()
    return UNKNOWN_COMMAND_MSG


def _handle_stats_case(cmd_args: list[str]) -> str:
    if len(cmd_args) == LEN_TWO:
        return stats_handler(cmd_args[1])
    return UNKNOWN_COMMAND_MSG


def match_case_handler(cmd_args: list[str]) -> str:
    result = UNKNOWN_COMMAND_MSG

    match cmd_args[0]:
        case "income":
            result = _handle_income_case(cmd_args)

        case "cost":
            result = _handle_cost_case(cmd_args)

        case "stats":
            result = _handle_stats_case(cmd_args)
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
