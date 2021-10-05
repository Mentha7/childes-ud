class Sentence(object):
    """docstring for Sentence"""

    __slots__ = ['speaker',
                 'tiers',
                 'gra',
                 'mor',
                 'chat_sent',
                 'clean',
                 'comments',
                 'sent_id',
                 'toks',
                ]

    def __init__(self,
                 speaker=None,
                 tiers=None,
                 gra=None,
                 mor=None,
                 chat_sent=None,
                 clean=None,
                 comments=None,
                 sent_id=None,
                 toks=None
                 ):
        self.speaker=speaker
        self.tiers=tiers
        self.gra=gra
        self.mor=mor
        self.chat_sent=chat_sent
        self.clean=clean
        self.comments=comments
        self.sent_id=sent_id
        self.toks=toks

    def __str__(self):
        fields = [str(getattr(self, x)) for x in self.__slots__[:]]
        return ("\n".join(fields))

    def text(self):
        tokens = [x.form for x in self.toks] if self.toks else []
        return " ".join(tokens)

    def get_sent_id(self):
        return self.sent_id

    def conllu_str(self, clear_mor=False, clear_gra=False, clear_misc=False, mute=False):
        s = ""
        if self.toks:
            for tok in self.toks:
                if mute:
                    s += "# " + tok.conllu_str(clear_mor, clear_gra, clear_misc)
                else:
                    s += tok.conllu_str(clear_mor, clear_gra, clear_misc)
        return s
