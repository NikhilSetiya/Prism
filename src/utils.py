"""Utility functions for configuration, logging, and execution context."""

import os
import re
import yaml
import json
import time
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from contextlib import contextmanager

# Load environment variables
load_dotenv()


class Config:
    """Load and validate configuration from YAML with environment variable interpolation."""
    
    @staticmethod
    def load(config_path: str = "config.yaml") -> Dict[str, Any]:
        """Load configuration from YAML file with environment variable substitution."""
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Replace ${VAR} with environment variables
        def replace_env(match):
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))
        
        pattern = r'\$\{([^}]+)\}'
        content = re.sub(pattern, replace_env, content)
        
        config = yaml.safe_load(content)
        return config
    
    @staticmethod
    def get(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
        """Get nested config value using dot notation (e.g., 'generator.model')."""
        keys = key_path.split('.')
        value = config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value


class ExecutionContext:
    """Manage execution lifecycle with cost tracking and timing."""
    
    def __init__(self, campaign_id: str):
        self.campaign_id = campaign_id
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.costs: list[float] = []
        self.timings: Dict[str, float] = {}
        self.errors: list[str] = []
        self.assets_generated = 0
        self.assets_reused = 0
        self.stage_timings: Dict[str, float] = {}
        
        # Hero + variations tracking
        self.hero_images_generated = 0
        self.hero_images_cached = 0
        self.variations_created = 0
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        if self.start_time and self.end_time:
            self.timings['total_execution'] = self.end_time - self.start_time
        return False
    
    def record_cost(self, amount: float):
        """Record a cost transaction."""
        self.costs.append(amount)
    
    def record_timing(self, operation: str, duration: float):
        """Record timing for an operation."""
        self.timings[operation] = duration
        
        # Aggregate by stage
        stage = operation.split('_')[0] if '_' in operation else operation
        self.stage_timings[stage] = self.stage_timings.get(stage, 0) + duration
    
    def record_error(self, error: str):
        """Record an error message."""
        self.errors.append(error)
    
    def get_total_cost(self) -> float:
        """Get total cost across all transactions."""
        return sum(self.costs)
    
    def get_report(self) -> Dict[str, Any]:
        """Generate execution report."""
        total_cost = self.get_total_cost()
        total_assets = self.assets_generated + self.assets_reused
        cache_efficiency = (self.assets_reused / total_assets * 100) if total_assets > 0 else 0.0
        
        # Calculate actual execution time
        execution_time = 0.0
        if self.start_time and self.end_time:
            execution_time = self.end_time - self.start_time
        elif self.start_time:
            execution_time = time.time() - self.start_time
        
        # Merge detailed and stage timings
        all_timings = {**self.timings, 'stage_timings': self.stage_timings}
        
        return {
            'campaign_id': self.campaign_id,
            'products_count': 0,  # Will be set by pipeline
            'assets_generated': self.assets_generated,
            'assets_reused': self.assets_reused,
            'total_cost': total_cost,
            'execution_time': execution_time,
            'cache_efficiency': cache_efficiency,
            'output_path': f"./output/{self.campaign_id}",
            'hero_images_generated': self.hero_images_generated,
            'hero_images_cached': self.hero_images_cached,
            'variations_created': self.variations_created,
            'errors': self.errors,
            'timings': all_timings
        }


class RateLimiter:
    """Token bucket rate limiter for API calls."""
    
    def __init__(self, max_per_minute: int):
        self.max_per_minute = max_per_minute
        self.tokens = max_per_minute
        self.last_refill = time.time()
        self.refill_rate = max_per_minute / 60.0  # tokens per second
    
    def acquire(self):
        """Acquire a token, blocking if necessary."""
        now = time.time()
        elapsed = now - self.last_refill
        
        # Refill tokens
        self.tokens = min(self.max_per_minute, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
        
        # Wait if no tokens available
        if self.tokens < 1:
            wait_time = (1 - self.tokens) / self.refill_rate
            time.sleep(wait_time)
            self.tokens = 0
        else:
            self.tokens -= 1


def ensure_dir(path: str):
    """Ensure directory exists, creating if necessary."""
    Path(path).mkdir(parents=True, exist_ok=True)


def load_json(path: str) -> Dict[str, Any]:
    """Load JSON file."""
    with open(path, 'r') as f:
        return json.load(f)


def save_json(data: Dict[str, Any], path: str):
    """Save data to JSON file."""
    ensure_dir(os.path.dirname(path))
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

