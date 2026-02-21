#!/usr/bin/env python3
"""
Main execution script
"""
from src.config import load_config
from src.db import Database
from src.scanner import ScannerFactory

def main():
    # Load configuration
    config_path = 'config.yaml'
    config = load_config(config_path)
    
    # Initialize database
    db = Database(config)
    db.initialize()
    
    # Initialize scanner
    scanner = ScannerFactory.get_scanner(config['scanner']['type'])
    results = scanner.scan()
    
    # Generate report
    report_renderer = ReportRenderer(config)
    report_renderer.render(results, config['report']['output_path'])

if __name__ == '__main__':
    main()

