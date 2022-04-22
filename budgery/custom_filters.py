def currency(amount: float):
	"Show a float as a currency amount."
	if amount < 0:
		return "-${:,.2f}".format(-1 * amount)
	return "${:,.2f}".format(amount)
