import collections
from dataclasses import dataclass
from typing import Iterable, List

from budgery.db import models

@dataclass
class BudgetEntryReport:
	entry: models.BudgetEntry
	net: float
	transactions: List

@dataclass
class BudgetCategoryReport:
	category: str
	entries: List[BudgetEntryReport]
	net: float

@dataclass
class UnbudgetedTransactionsReport:
	category: str
	transactions: List[models.Transaction]
	net: float

@dataclass
class BudgetReport:
	total_in: float
	total_out: float
	net: float
	entries_by_category: List[BudgetCategoryReport]
	unbudgeted_transactions: List[UnbudgetedTransactionsReport]

def budget_report(
		entries: Iterable[models.BudgetEntry],
		transactions: Iterable[models.Transaction],
	) -> BudgetReport:
	budget_category_set = set(entry.category for entry in entries)
	budget_categories = {
		category: collections.defaultdict(list) for category in budget_category_set
	}
	for entry in entries:
		budget_categories[entry.category].append({
			"amount": entry.amount,
			"name": entry.name,
			"net": 0,
		})
	
	transactions_by_category = collections.defaultdict(list)
	for transaction in transactions:
		transactions_by_category[transaction.category].append(transaction)
	budget_entry_reports_by_category = collections.defaultdict(list)
	for entry in entries:
		# Note - we map transactions by budget entry name, not by budget entry category. Different types of categories between budget entries and transactions.
		my_transactions = transactions_by_category[entry.name]
		budget_entry_reports_by_category[entry.category].append(BudgetEntryReport(
			entry=entry,
			net=sum(t for t in my_transactions),
			transactions=my_transactions,
		))
	category_reports_by_name = collections.defaultdict(list)
	for budget_category in budget_categories:
		my_entry_reports = budget_entry_reports_by_category[budget_category]
		category_reports_by_name.append(BudgetCategoryReport(
			category=category,
			entries=my_entry_reports,
			net=sum(report.entry.amount for report in my_entry_reports),
		))
	unbudgeted_transactions = {}
	for category, transactions in transactions_by_category.items():
		if category not in budget_categories:
			unbudgeted_transactions[category] = transactions
	total_in = sum(e for e in entries if e.amount > 0)
	total_out = sum(e for e in entries if e.amount < 0)
	entries_by_category = sorted(category_reports_by_name.values(), key=lambda r: r.category)
	unbudgeted_transactions = [
		UnbudgetedTransactionsReport(
			category=category,
			net=sum(t.amount for t in transactions),
			transactions=transactions,
		) for category, transactions in unbudgeted_transactions.items()
	]

	return BudgetReport(
		total_in=total_in,
		total_out=total_out,
		net=total_in + total_out,
		entries_by_category=entries_by_category,
		unbudgeted_transactions=unbudgeted_transactions,
	)
