class Widget(object):
	def __init__(self, config_data):
		self._config = config_data

	@property
	def config_data(self):
		return self._config_data

	def update(self, instrument_data):
		raise Exception(NotImplemented)

	def render(self, cctx):
		raise Exception(NotImplemented)
