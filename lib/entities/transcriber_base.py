
from .base import CBase
class CTranscriber(CBase):
    classname = "transcriber_base";

    def __init__(self):
        self._initialize_files();

    def _initialize_files(self):
        return NotImplementedError;