def currency(amount: float):
	"Show a float as a currency amount."
	return "${:,.2f}".format(amount)
