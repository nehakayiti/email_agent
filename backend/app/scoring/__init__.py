"""
Email Scoring System Package

This package provides a comprehensive, modular email attention scoring system.
"""

from app.scoring.config import get_config, current_config
from app.scoring.engine import EmailScoringEngine, ScoringEngineFactory
from app.scoring.strategies import EnhancedScoringStrategy, SimpleScoringStrategy
from app.scoring.cache_providers import create_cache_provider
from app.scoring.debugger import EmailScoringDebugger

__all__ = [
    'get_config',
    'current_config', 
    'EmailScoringEngine',
    'ScoringEngineFactory',
    'EnhancedScoringStrategy',
    'SimpleScoringStrategy',
    'create_cache_provider',
    'EmailScoringDebugger'
]