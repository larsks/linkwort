class RuleViolation(Exception):
    def __init__(self, ruleid, filename, lineno, text):
        self.ruleid = ruleid
        self.filename = filename
        self.lineno = lineno
        self.text = text

    def __str__(self):
        return '{ruleid} at {filename}:{lineno}'.format(
            ruleid=self.ruleid,
            filename=self.filename,
            lineno=self.lineno)

    def __repr__(self):
        return str(self)

