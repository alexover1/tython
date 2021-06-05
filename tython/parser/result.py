############################################
# PARSE RESULT
############################################


class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, res):
        """
        Takes in ParseResult and extracts and returns node
        """
        if isinstance(res, ParseResult):
            if res.error:
                self.error = res.error
            return res.node

        return res

    def success(self, node):
        """
        Takes in node and returns node, None
        """
        self.node = node
        return self

    def failure(self, error):
        """
        Takes node and returns None, error
        """
        self.error = error
        return self
