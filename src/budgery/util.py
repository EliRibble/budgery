"Dumping ground for functions."
from typing import Iterable, Mapping

from budgery.db import models

def transaction_count_by_budget_id(
		budgets: Iterable[models.Budget],
		transactions: Iterable[models.Transaction],
	) -> Mapping[int, int]:
	"Given a list of budgets and transactions figure out how many transactions are in each budget time span."
	spans = [(
		b.start_date,
		b.end_date,
	) for b in budgets]
	counts = [0 for b in budgets]
	# Add a placeholder for "no matching budget"
	spans += [(None, None)]
	counts += [0]
	for t in transactions:
		for i, span in enumerate(spans):
			if span[0] is None:
				counts[-1] += 1
				break
			elif span[0] <= t.at.date() < span[1]:
				counts[i] += 1
				break

	result = {b.id: counts[i] for i, b in enumerate(budgets)}
	result[None] = counts[-1]
	return result
