import logging
import sys
from typing import Optional

_logger: Optional[logging.Logger] = None


def get_logger(name: str = "gitlab_ml") -> logging.Logger:
    """Get or create a logger instance."""
    global _logger
    
    if _logger is None:
        _logger = logging.getLogger(name)
        _logger.setLevel(logging.INFO)
        
        # Create console handler
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        _logger.addHandler(handler)
    
    return _logger


def setup_logging(verbose: bool = False) -> None:
    """Configure logging settings."""
    logger = get_logger()
    
    if verbose:
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG) 