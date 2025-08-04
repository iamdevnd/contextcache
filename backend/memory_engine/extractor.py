import spacy
from typing import List, Optional, Tuple
from ..db.models import Triple
import logging

logger = logging.getLogger(__name__)

class TripleExtractor:
    def __init__(self, model_name: str = "en_core_web_sm"):
        """Initialize the triple extractor with spaCy model"""
        try:
            self.nlp = spacy.load(model_name)
            self.enabled = True
            logger.info(f"Loaded spaCy model: {model_name}")
        except OSError:
            logger.warning(f"spaCy model {model_name} not found. Triple extraction disabled.")
            self.enabled = False
            self.nlp = None
    
    def extract_triples(self, text: str, context: Optional[str] = None) -> List[Triple]:
        """Extract subject-verb-object triples from text"""
        if not self.enabled:
            return []
        
        doc = self.nlp(text)
        triples = []
        
        # Extract triples using dependency parsing
        for token in doc:
            if token.pos_ == "VERB":
                subject = None
                object_ = None
                
                # Find subject
                for child in token.children:
                    if child.dep_ in ("nsubj", "nsubjpass"):
                        subject = self._get_compound_phrase(child)
                    elif child.dep_ in ("dobj", "pobj", "attr"):
                        object_ = self._get_compound_phrase(child)
                
                # If we have both subject and object, create a triple
                if subject and object_:
                    triple = Triple(
                        subject=subject,
                        verb=token.lemma_,
                        object=object_,
                        context=context,
                        confidence=self._calculate_confidence(token)
                    )
                    triples.append(triple)
        
        return triples
    
    def _get_compound_phrase(self, token) -> str:
        """Get the full phrase including compound words"""
        phrase_tokens = [token]
        
        # Get compound tokens
        for child in token.children:
            if child.dep_ in ("compound", "amod", "det"):
                phrase_tokens.append(child)
        
        # Sort by position and join
        phrase_tokens.sort(key=lambda x: x.i)
        return " ".join([t.text for t in phrase_tokens])
    
    def _calculate_confidence(self, verb_token) -> float:
        """Calculate confidence score for the triple"""
        # Simple confidence based on dependency tree completeness
        confidence = 0.5
        
        # Boost confidence if subject and object are clear
        has_clear_subject = any(child.dep_ == "nsubj" for child in verb_token.children)
        has_clear_object = any(child.dep_ in ("dobj", "pobj") for child in verb_token.children)
        
        if has_clear_subject:
            confidence += 0.25
        if has_clear_object:
            confidence += 0.25
        
        return confidence
    
    def extract_entities(self, text: str) -> List[Tuple[str, str]]:
        """Extract named entities from text"""
        if not self.enabled:
            return []
        
        doc = self.nlp(text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        return entities

# Singleton instance
_extractor_instance = None

def get_triple_extractor() -> TripleExtractor:
    global _extractor_instance
    if _extractor_instance is None:
        from ..config import get_settings
        settings = get_settings()
        _extractor_instance = TripleExtractor(settings.spacy_model)
    return _extractor_instance
