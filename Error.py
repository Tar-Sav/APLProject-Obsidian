class Error:
    def __init__(self, errorName, errorDetail):
        self.errorName = errorName
        self.errorDetail = errorDetail

    def errorString(self):
        string = f"{self.errorName}: {self.errorDetail}"
        return string

class IllegalToken(Error):
    def __init__(self, details):
        super().__init__("Illegal Token", details)

class SemanticError(Error):
    def __init__(self, detail):
        super().__init__("Semantic Error", detail)

class RuntimeErr(Error):
    def __init__(self, detail):
        super().__init__("Runtime Error", detail)