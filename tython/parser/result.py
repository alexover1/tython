############################################
# PARSE RESULT
############################################


class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0

    def register_advancement(self):
        self.advance_count += 1

    def register(self, res):
        """
        Takes in ParseResult and extracts and returns node
        """
        self.advance_count += res.advance_count
        if res.error:
            self.error = res.error
        return res.node

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
        if not self.error or self.advance_count == 0:
            self.error = error
        return self
