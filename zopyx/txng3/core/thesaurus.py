###########################################################################
# TextIndexNG V 3
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

import os
import re
from zope.interface import implementer
from zopyx.txng3.core.interfaces import IThesaurus

th_dir = os.path.join(os.path.dirname(__file__), 'data', 'thesaurus')

# match the encoding header
enc_reg = re.compile('#\s*encoding\s*=\s*([\w\-]+)')


def readThesaurus(language, casefolding=True, filename=None):
    """ read thesaurus file """

    synonyms = {}
    terms = {}
    encoding = None

    if filename is None:
        filename = os.path.join(th_dir, '%s.txt' % language)

    if not os.path.exists(filename):
        raise ValueError('No thesaurus file for "%s" found' % language)

    for idx, l in enumerate(open(filename, 'r', encoding='iso-8859-15')):
        if not l.strip():
            continue

        mo = enc_reg.match(l)
        if mo:
            encoding = mo.group(1)
            continue

        if l.startswith('#'):
            continue

        term, words = l.split(' ', 1)
        if encoding:
            term = term.strip()
            words = [w.strip() for w in words.split(',')]
            if casefolding:
                term = term.lower()
                words = [w.lower() for w in words]
            synonyms[idx] = [term] + words
            for t in synonyms[idx]:
                if t in terms:
                    terms[t].append(idx)
                else:
                    terms[t] = [idx]

        else:
            raise ValueError(
                "Thesaurus file %s has no 'encoding' parameter specified" % filename)

    return synonyms, terms


@implementer(IThesaurus)
class Thesaurus:


    def __init__(self, language, casefolding=True, filename=None):
        self._language = language
        self._filename = filename
        self._synonyms = {}  # 1: [word1, word2]
        self._terms = {}  # word1: [1]
        self._casefolding = casefolding
        self._loaded = False

    def _load(self):
        self._synonyms, self._terms = readThesaurus(
            self._language, self._casefolding, self._filename)
        self._loaded = True

    def getTermsFor(self, word):
        """ return a list of similiar terms for a the given word in a given language"""
        if not self._loaded:
            self._load()
        if self._casefolding:
            word = word.lower()
        result = set()
        for synonymIdx in self._terms.get(word, []):
            result.update(self._synonyms.get(synonymIdx, []))

        if result:
            result.remove(word)

        return result and list(result) or None

    def getLanguage(self):
        """ return the language of the thesaurus """
        return self._language

    def getSize(self):
        if not self._loaded:
            self._load()
        return len(self._terms)


GermanThesaurus = Thesaurus('de')
