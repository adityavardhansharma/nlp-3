from spellchecker import SpellChecker

class SpellCorrector:
    def __init__(self):
        self.spell = SpellChecker()
    def correct(self, text: str) -> str:
        tokens = text.split()
        corrected = []
        for w in tokens:
            # only correct alphabetical tokens
            if w.isalpha():
                corrected.append(self.spell.correction(w) or w)
            else:
                corrected.append(w)
        return " ".join(corrected)
