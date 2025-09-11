#!/usr/bin/env python3
"""
ASI Core - Semantic Search System
Deterministisches Embedding System für ASI Memory Retrieval
"""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

__all__ = [
    'ASIEmbeddingGenerator',
    'ASISemanticSearch'
]


class ASIEmbeddingGenerator:
    """
    Generiert deterministische 128-byte Embeddings für ASI Texte.
    Nutzt SHA-512 Hashing für konsistente Ergebnisse.
    """
    
    def __init__(self):
        """Initialisiert den Embedding Generator."""
        self.algorithm = 'sha512'
        self.embedding_size = 128
        
    def generate_embedding(self, text: str) -> bytes:
        """
        Generiert ein 128-byte Embedding für den gegebenen Text.
        
        Args:
            text: Der zu verarbeitende Text
            
        Returns:
            128 bytes deterministisches Embedding
        """
        if not text or not isinstance(text, str):
            raise ValueError("Text muss ein nicht-leerer String sein")
            
        # Normalisiere Text für konsistente Embeddings
        normalized_text = text.strip().lower()
        
        # Generiere SHA-512 Hash (64 bytes)
        hash_obj = hashlib.sha512(normalized_text.encode('utf-8'))
        hash_bytes = hash_obj.digest()
        
        # Erweitere auf 128 bytes durch doppeltes Hashing
        extended_hash = hashlib.sha512(hash_bytes + normalized_text.encode('utf-8')).digest()
        
        # Kombiniere für 128 bytes
        embedding = hash_bytes + extended_hash
        
        return embedding[:self.embedding_size]
    
    def get_embedding_info(self) -> Dict:
        """
        Gibt Informationen über den Embedding Generator zurück.
        
        Returns:
            Dictionary mit Generator-Informationen
        """
        return {
            'algorithm': self.algorithm,
            'embedding_size': self.embedding_size,
            'deterministic': True,
            'version': '1.0'
        }


class ASISemanticSearch:
    """
    Semantic Search System für ASI Memory.
    Speichert und durchsucht Embeddings mit lokaler Cache-Funktionalität.
    """
    
    def __init__(self, embedding_generator: Optional[ASIEmbeddingGenerator] = None, cache_file: Optional[str] = None):
        """
        Initialisiert das Semantic Search System.
        
        Args:
            embedding_generator: ASI Embedding Generator (wird automatisch erstellt wenn None)
            cache_file: Pfad zur Cache-Datei (default: data/search/embedding_cache.json)
        """
        self.embedding_generator = embedding_generator or ASIEmbeddingGenerator()
        
        # Cache-Datei Setup
        if cache_file is None:
            cache_dir = Path('data/search')
            cache_dir.mkdir(parents=True, exist_ok=True)
            self.cache_file = cache_dir / 'embedding_cache.json'
        else:
            self.cache_file = Path(cache_file)
            
        # Lade bestehenden Cache
        self._load_cache()
        
    def _load_cache(self):
        """Lädt den Embedding Cache von der Festplatte."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cache = data.get('embeddings', {})
                    self.metadata = data.get('metadata', {})
            else:
                self.cache = {}
                self.metadata = {}
                
        except Exception as e:
            logger.warning(f"Fehler beim Laden des Caches: {e}")
            self.cache = {}
            self.metadata = {}
            
    def _save_cache(self):
        """Speichert den Embedding Cache auf die Festplatte."""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            cache_data = {
                'embeddings': self.cache,
                'metadata': self.metadata,
                'last_updated': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Caches: {e}")
    
    def store_embedding(self, cid: str, embedding: bytes, text_preview: str):
        """
        Speichert ein Embedding mit Metadaten im Cache.
        
        Args:
            cid: Content Identifier (IPFS CID oder ähnlich)
            embedding: Das 128-byte Embedding
            text_preview: Kurzer Textvorschau für Debugging
        """
        if len(embedding) != 128:
            raise ValueError("Embedding muss genau 128 bytes haben")
            
        # Konvertiere bytes zu hex string für JSON Serialisierung
        embedding_hex = embedding.hex()
        
        self.cache[cid] = {
            'embedding': embedding_hex,
            'text_preview': text_preview[:200],  # Begrenze Preview
            'created_at': datetime.now().isoformat(),
            'size_bytes': len(embedding)
        }
        
        # Aktualisiere Metadaten
        self.metadata['total_embeddings'] = len(self.cache)
        self.metadata['last_added'] = cid
        
        self._save_cache()
        logger.debug(f"Embedding für CID {cid} gespeichert")
    
    def search_ASI_memory(self, query: str, num_results: int = 10) -> List[Dict]:
        """
        Durchsucht die ASI Memory basierend auf semantischer Ähnlichkeit.
        
        Args:
            query: Suchanfrage als Text
            num_results: Anzahl zurückzugebender Ergebnisse
            
        Returns:
            Liste von Ergebnissen mit CID, Similarity Score und Preview
        """
        if not query.strip():
            return []
            
        # Generiere Query Embedding
        query_embedding = self.embedding_generator.generate_embedding(query)
        
        results = []
        
        for cid, entry in self.cache.items():
            try:
                # Konvertiere hex string zurück zu bytes
                stored_embedding = bytes.fromhex(entry['embedding'])
                
                # Berechne Similarity (vereinfacht: Hamming Distance)
                similarity = self._calculate_similarity(query_embedding, stored_embedding)
                
                results.append({
                    'cid': cid,
                    'similarity': similarity,
                    'text_preview': entry['text_preview'],
                    'created_at': entry['created_at']
                })
                
            except Exception as e:
                logger.warning(f"Fehler bei CID {cid}: {e}")
                continue
        
        # Sortiere nach Similarity (höher = ähnlicher)
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        return results[:num_results]
    
    def _calculate_similarity(self, embedding1: bytes, embedding2: bytes) -> float:
        """
        Berechnet Ähnlichkeit zwischen zwei Embeddings.
        
        Args:
            embedding1: Erstes Embedding (128 bytes)
            embedding2: Zweites Embedding (128 bytes)
            
        Returns:
            Similarity Score zwischen 0.0 und 1.0
        """
        if len(embedding1) != len(embedding2):
            return 0.0
            
        # Hamming Distance basierte Similarity
        matching_bits = sum(
            bin(b1 ^ b2).count('0') for b1, b2 in zip(embedding1, embedding2)
        )
        
        total_bits = len(embedding1) * 8
        similarity = matching_bits / total_bits
        
        return similarity
    
    def get_cache_stats(self) -> Dict:
        """
        Gibt Statistiken über den Embedding Cache zurück.
        
        Returns:
            Dictionary mit Cache-Statistiken
        """
        total_size = sum(
            len(bytes.fromhex(entry['embedding'])) 
            for entry in self.cache.values()
        )
        
        return {
            'total_embeddings': len(self.cache),
            'cache_size_bytes': total_size,
            'cache_file': str(self.cache_file),
            'last_updated': self.metadata.get('last_updated'),
            'generator_info': self.embedding_generator.get_embedding_info()
        }
