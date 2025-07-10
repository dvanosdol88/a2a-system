"""Production-ready logging configuration for A2A System"""

import os
import sys
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path

from config.settings import Config


class A2ALogger:
    """Centralized logging configuration for all A2A components"""
    
    # Log format templates
    FORMATS = {
        'detailed': '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        'simple': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'json': '{"time":"%(asctime)s","name":"%(name)s","level":"%(levelname)s","file":"%(filename)s","line":%(lineno)d,"message":"%(message)s"}'
    }
    
    @classmethod
    def setup_logging(cls, component_name: str = 'a2a') -> logging.Logger:
        """Set up logging for a component"""
        # Create logger
        logger = logging.getLogger(component_name)
        logger.setLevel(getattr(logging, Config.LOG_LEVEL))
        
        # Remove existing handlers
        logger.handlers = []
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            cls.FORMATS['simple'] if Config.ENVIRONMENT == 'development' else cls.FORMATS['detailed']
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_dir / f'{component_name}.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(cls.FORMATS['detailed'])
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            filename=log_dir / f'{component_name}_errors.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)
        
        # Production syslog handler (optional)
        if Config.ENVIRONMENT == 'production' and sys.platform != 'win32':
            try:
                syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')
                syslog_handler.setLevel(logging.WARNING)
                syslog_formatter = logging.Formatter(f'{component_name}: %(levelname)s - %(message)s')
                syslog_handler.setFormatter(syslog_formatter)
                logger.addHandler(syslog_handler)
            except Exception:
                pass  # Syslog not available
        
        return logger
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get a logger instance"""
        return logging.getLogger(name)


class RequestLogger:
    """Specialized logger for API requests"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_request(self, method: str, path: str, status: int, duration_ms: int, **kwargs):
        """Log API request with structured data"""
        extra = {
            'method': method,
            'path': path,
            'status': status,
            'duration_ms': duration_ms,
            **kwargs
        }
        
        if status >= 500:
            self.logger.error(f"{method} {path} - {status} ({duration_ms}ms)", extra=extra)
        elif status >= 400:
            self.logger.warning(f"{method} {path} - {status} ({duration_ms}ms)", extra=extra)
        else:
            self.logger.info(f"{method} {path} - {status} ({duration_ms}ms)", extra=extra)


class PerformanceLogger:
    """Logger for performance metrics"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_metric(self, metric_name: str, value: float, unit: str = '', **tags):
        """Log performance metric"""
        tags_str = ' '.join(f'{k}={v}' for k, v in tags.items())
        self.logger.info(f"METRIC: {metric_name}={value}{unit} {tags_str}")


# Convenience functions
def setup_component_logging(component: str) -> logging.Logger:
    """Quick setup for component logging"""
    return A2ALogger.setup_logging(component)


def get_request_logger(component: str) -> RequestLogger:
    """Get request logger for component"""
    logger = A2ALogger.get_logger(component)
    return RequestLogger(logger)


def get_performance_logger(component: str) -> PerformanceLogger:
    """Get performance logger for component"""
    logger = A2ALogger.get_logger(component)
    return PerformanceLogger(logger)