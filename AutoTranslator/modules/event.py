class EventVariable:
    def __init__(self, value, name=None):
        self._value = value
        self._callback = None
        self._name = name  # ← 追加

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if new_value != self._value:
            self._value = new_value
            if self._callback:
                if self._name:
                    self._callback(self._name, new_value)
                else:
                    self._callback(new_value)

    def set_callback(self, callback):
        self._callback = callback
