from transformers import pipeline
import torch
from typing import Dict, List, Optional
import json
from pathlib import Path

def load_config() -> Dict:
    """Load configuration from config file"""
    config_path = Path(__file__).parent / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}
