"""
:mod:`textacy.text_stats.api`: Compute a variety of text statistics for documents.
"""
import inspect
import logging
from typing import Dict, Literal, Optional, Tuple

from spacy.tokens import Doc, Token

from .. import constants, errors, extract
from . import basics, diversity, morph, readability


LOGGER = logging.getLogger(__name__)

DiversityNameType = Literal["ttr", "log-ttr", "segmented-ttr", "mtld", "hdd"]
ReadabilityNameType = Literal[
    "automated-readability-index",
    "automatic-arabic-readability-index",
    "coleman-liau-index",
    "flesch-kincaid-grade-level",
    "flesch-reading-ease",
    "gulpease-index",
    "gunning-fog-index",
    "lix",
    "mu-legibility-index",
    "perspicuity-index",
    "smog-index",
    "wiener-sachtextformel",
]


class TextStats:
    """
    Class to compute a variety of basic, readability, morphological, and lexical diversity
    statistics for a given document.

    .. code-block:: pycon

        >>> text = next(textacy.datasets.CapitolWords().texts(limit=1))
        >>> doc = textacy.make_spacy_doc(text, lang="en_core_web_sm")
        >>> ts = textacy.text_stats.TextStats(doc)
        >>> ts.n_words
        137
        >>> ts.n_unique_words
        81
        >>> ts.entropy
        6.02267943673824
        >>> ts.readability("flesch-kincaid-grade-level")
        11.40259124087591
        >>> ts.diversity("ttr")
        0.5912408759124088

    Some readability stats vary by language or are designed for use with
    specific languages:

    .. code-block:: pycon

        >>> text = (
        ...     "Muchos años después, frente al pelotón de fusilamiento, "
        ...     "el coronel Aureliano Buendía había de recordar aquella tarde remota "
        ...     "en que su padre lo llevó a conocer el hielo."
        ... )
        >>> doc = textacy.make_spacy_doc(text, lang="es_core_news_sm")
        >>> ts = textacy.text_stats.TextStats(doc)
        >>> ts.readability("perspicuity-index")
        56.46000000000002
        >>> ts.readability("mu-legibility-index")
        71.18644067796609

    Each of these stats have stand-alone functions in :mod:`textacy.text_stats.basics` ,
    :mod:`textacy.text_stats.readability` , and :mod:`textacy.text_stats.diversity`
    with more detailed info and links in the docstrings -- when in doubt, read the docs!

    Args:
        doc: A text document tokenized and (optionally) sentence-segmented by spaCy.
    """

    def __init__(self, doc: Doc):
        self.doc = doc
        self.lang: str = doc.lang_
        self.words: Tuple[Token, ...] = tuple(
            extract.words(doc, filter_punct=True, filter_stops=False, filter_nums=False)
        )
        self._n_sents: Optional[int] = None
        self._n_words: Optional[int] = None
        self._n_unique_words: Optional[int] = None
        self._n_long_words: Optional[int] = None
        self._n_chars_per_word: Optional[Tuple[int, ...]] = None
        self._n_chars: Optional[int] = None
        self._n_syllables_per_word: Optional[Tuple[int, ...]] = None
        self._n_syllables: Optional[int] = None
        self._n_monosyllable_words: Optional[int] = None
        self._n_polysyllable_words: Optional[int] = None
        self._entropy: Optional[float] = None

    @property
    def n_sents(self) -> int:
        """
        Number of sentences in document.

        See Also:
            :func:`textacy.text_stats.basics.n_sents()`
        """
        if self._n_sents is None:
            self._n_sents = basics.n_sents(self.doc)
        return self._n_sents

    @property
    def n_words(self) -> int:
        """
        Number of words in document.

        See Also:
            :func:`textacy.text_stats.basics.n_words()`
        """
        if self._n_words is None:
            self._n_words = basics.n_words(self.words)
        return self._n_words

    @property
    def n_unique_words(self) -> int:
        """
        Number of *unique* words in document.

        See Also:
            :func:`textacy.text_stats.basics.n_unique_words()`
        """
        if self._n_unique_words is None:
            self._n_unique_words = basics.n_unique_words(self.words)
        return self._n_unique_words

    @property
    def n_long_words(self) -> int:
        """
        Number of long words in document.

        See Also:
            :func:`textacy.text_stats.basics.n_long_words()`
        """
        # TODO: should we vary char threshold by lang?
        if self._n_long_words is None:
            self._n_long_words = basics.n_long_words(self.words, min_n_chars=7)
        return self._n_long_words

    @property
    def n_chars_per_word(self) -> Tuple[int, ...]:
        """
        Number of characters for each word in document.

        See Also:
            :func:`textacy.text_stats.basics.n_chars_per_word()`
        """
        if self._n_chars_per_word is None:
            self._n_chars_per_word = basics.n_chars_per_word(self.words)
        return self._n_chars_per_word

    @property
    def n_chars(self) -> int:
        """
        Total number of characters in document.

        See Also:
            :func:`textacy.text_stats.basics.n_chars()`
        """
        if self._n_chars is None:
            self._n_chars = basics.n_chars(self.words)
        return self._n_chars

    @property
    def n_syllables_per_word(self) -> Tuple[int, ...]:
        """
        Number of syllables for each word in document.

        See Also:
            :func:`textacy.text_stats.basics.n_syllables_per_word()`
        """
        if self._n_syllables_per_word is None:
            self._n_syllables_per_word = basics.n_syllables_per_word(
                self.words, lang=self.lang
            )
        return self._n_syllables_per_word

    @property
    def n_syllables(self) -> int:
        """
        Total number of syllables in document.

        See Also:
            :func:`textacy.text_stats.basics.n_syllables()`
        """
        if self._n_syllables is None:
            self._n_syllables = basics.n_syllables(self.words, lang=self.lang)
        return self._n_syllables

    @property
    def n_monosyllable_words(self) -> int:
        """
        Number of monosyllobic words in document.

        See Also:
            :func:`textacy.text_stats.basics.n_monosyllable_words()`
        """
        if self._n_monosyllable_words is None:
            self._n_monosyllable_words = basics.n_monosyllable_words(
                self.words, lang=self.lang
            )
        return self._n_monosyllable_words

    @property
    def n_polysyllable_words(self) -> int:
        """
        Number of polysyllobic words in document.

        See Also:
            :func:`textacy.text_stats.basics.n_polysyllable_words()`
        """
        # TODO: should we vary syllable threshold by lang?
        if self._n_polysyllable_words is None:
            self._n_polysyllable_words = basics.n_polysyllable_words(
                self.words, lang=self.lang, min_n_syllables=3
            )
        return self._n_polysyllable_words

    @property
    def entropy(self) -> float:
        """
        Entropy of words in document.

        See Also:
            :func:`textacy.text_stats.basics.entropy()`
        """
        if self._entropy is None:
            self._entropy = basics.entropy(self.words)
        return self._entropy

    @property
    def morph_counts(self) -> Dict[str, Dict[str, int]]:
        """
        Number of times each value for a given morphological label appears in document.

        See Also:
            :func:`textacy.text_stats.morph.get_morph_label_counts()`
        """
        # NOTE: afaict there is absolutely no way to get the spacy language pipeline
        # used to produce a given document from the document itself
        # so, we can't get the lang-specific set of morph labels here
        # and instead just scan through all of the UD v2 default labels
        # then filter out those that don't have any values in the document
        # not ideal, but it's what we're stuck with
        mcs = {
            label: morph.get_morph_label_counts(label, self.doc)
            for label in constants.UD_V2_MORPH_LABELS
        }
        return {
            morph_label: value_counts
            for morph_label, value_counts in mcs.items()
            if value_counts
        }

    def readability(self, name: ReadabilityNameType, **kwargs) -> float:
        """
        Compute a measure of text readability using a method with specified ``name``.

        Higher values => more difficult text for the following methods:

        - automated readability index
        - automatic arabic readability index
        - colman-liau index
        - flesch-kincaid grade level
        - gunning-fog index
        - lix
        - smog index
        - wiener-sachtextformel

        Higher values => less difficult text for the following methods:

        - flesch reading ease
        - gulpease index
        - mu legibility index
        - perspicuity index

        See Also:
            :mod:`textacy.text_stats.readability`
        """
        # in case users prefer "flesch-reading-ease" or "flesch reading ease"
        # to the underscored func-standard name "flesch_reading_ease"
        name = name.replace("-", "_").replace(" ", "_")
        try:
            func = getattr(readability, name)
        except AttributeError:
            raise ValueError(
                errors.value_invalid_msg(
                    "name",
                    name,
                    [
                        name
                        for name, _ in inspect.getmembers(
                            readability, inspect.isfunction
                        )
                        if not name.startswith("_")
                    ],
                )
            )
        return func(self.doc, **kwargs)

    def diversity(self, name: DiversityNameType, **kwargs) -> float:
        """
        Compute a measure of lexical diversity using a method with specified ``name`` ,
        optionally specifying method variants and parameters.

        Higher values => higher lexical diversity.

        See Also:
            :mod:`textacy.text_stats.diversity`
        """
        # in case users prefer "log-ttr" or "log ttr"
        # to the underscored func-standard name "log_ttr"
        name = name.replace("-", "_").replace(" ", "_")
        try:
            func = getattr(diversity, name)
        except AttributeError:
            raise ValueError(
                errors.value_invalid_msg(
                    "name",
                    name,
                    [
                        name
                        for name, _ in inspect.getmembers(diversity, inspect.isfunction)
                        if not name.startswith("_")
                    ],
                )
            )
        return func(self.words, **kwargs)
