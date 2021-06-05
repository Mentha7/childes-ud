class ChatToken(object):
    """docstring for ChatToken"""
    def __init__(self, arg):
        self.arg = arg

    def index(self):
        pass

    def surface(self):
        pass

    def token(self):
        pass

    def lemma(self):
        pass

    def mor(self):
        pass

    def gra(self):
        pass

    def pos(self):
        pass

    def head(self):
        pass


class ChatLabel(object):
    """docstring for ChatLabel"""
    def __init__(self, arg):
        self.arg = arg

    def form(self):
        pass


class ChatSentence(object):
    """Holds a Chat sentence.
    Attributes:
        items   - tokens and labels in the sentence (ordered)
        tokens   - tokens in the sentence
        # labels   - labels in the sentence
        speaker   - the participant whouttered the sentence
    """
    def __init__(self, arg):
        self.arg = arg

    def tokens(self):
        pass

    def items(self):
        pass

    def __str__(self):
        pass

    def __len__(self):
        pass


class ChatMeta(object):
    """docstring for ChatMeta"""
    def __init__(self, arg):
        self.arg = arg
