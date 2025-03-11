class perform_arbitrage_err:
	def __init__(self, arb_identified: bool, executed: bool):
		self._arb_identified: bool = arb_identified
		self._executed: bool = executed

	def arb_identified(self) -> bool:
		return self._arb_identified

	def executed(self) -> bool:
		return self._executed