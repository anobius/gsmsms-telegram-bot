import threading

class CBase(object):
	classname = "base"
	_local = threading.local()

	def normalizeToUnicode(self, somestringuni):
		try:
			return somestringuni.decode('idna');
		except:
			return somestringuni.decode('utf-8') if type(somestringuni) == str else somestringuni;

	def setLastError(self,message):
		self._local.errMsg = message;

	def getLastError(self):
		try:
			return self._local.errMsg;
		except:
			return "Nuthin m8"

	def getLastExtendedInfo(self):
		try:
			return self._local.dbgInfo;
		except:
			return None;

	def _setLastExtendedInfo(self,message):
		self._local.dbgInfo = message;

	def setExtraData(self,Id,data):
		try:
			self._local.data[Id] = data;
		except:
			self._local.data = {Id:data};

	def getExtraData(self,Id):
		try:
			rVal = self._local.data[Id];
			del self._local.data[Id];
			return rVal;
		except:
			return None;





