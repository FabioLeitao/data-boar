from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re
import json
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import threading
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///compliance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def init_db():
    with app.app_context():
        db.create_all()

# Database Models
class DatabaseConfig(db.Model):
    __tablename__ = 'database_configs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    host = db.Column(db.String(100), nullable=False)
    port = db.Column(db.Integer, default=5432)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    database_name = db.Column(db.String(100), nullable=False)
    driver = db.Column(db.String(50), default='psycopg2')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scans = db.relationship('ScanResult', backref='database_config', lazy=True)

class ScanResult(db.Model):
    __tablename__ = 'scan_results'
    id = db.Column(db.Integer, primary_key=True)
    database_config_id = db.Column(db.Integer, db.ForeignKey('database_configs.id'), nullable=False)
    scan_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='pending')
    findings = db.Column(db.Text, nullable=True)
    report_file = db.Column(db.String(200), nullable=True)

class PersonalDataPattern:
    EMAIL = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE = r'\(?\d{2}\)?[\s-]?\d{4}[\s-]?\d{4}'
    CPF = r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}'
    RG = r'\d{2}[\.\-]?\d{3}[\.\-]?\d{3}[\.\-]?\d{2}'
    NAME = r'(?:[\'A-ZÀ-ú]+[\s-]*){2,})'
    CREDIT_CARD = r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}'

# Compliance requirements (can be extended)
COMPLIANCE_REQUIREMENTS = {
    'data_encryption': True,
    'consent_obtained': True,
    'data_minimization': True,
    'data_retention': True,
    'access_controls': True,
    'data_subject_rights': True
}

# Initialize database
def init_db():
    db.create_all()

# PDF Report Generation
def generate_pdf_report(findings):
    filename = f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    # Create PDF content
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = Paragraph("Compliance Scan Report", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 0.5 * inch))
    
    # Summary
    summary = Paragraph("Summary", styles['Heading2'])
    story.append(summary)
    
    # Compliance status
    compliance_status = Paragraph(
        f"Compliance Status: "
        f"{'Compliant' if all(COMPLIANCE_REQUIREMENTS.values()) else 'Non-Compliant'}", 
        styles['Normal']
    )
    story.append(compliance_status)
    
    # Findings
    findings_title = Paragraph("Findings", styles['Heading2'])
    story.append(findings_title)
    story.append(Spacer(1, 0.5 * inch))
    
    # List findings
    for i, finding in enumerate(findings, 1):
        finding_text = Paragraph(f"{i}. {finding}", styles['Normal'])
        story.append(finding_text)
        story.append(Spacer(1, 0.2 * inch))
    
    # Generate PDF
    doc.build(story)
    return filename

# Scan Worker Thread
def scan_worker(scan_id):
    from .models import ScanResult
    scan = ScanResult.query.get(scan_id)
    
    if not scan:
        logger.error("Scan not found")
        return
    
    # Simulate scanning process (in a real app, this would connect to databases)
    logger.info("Starting scan simulation...")
    
    scan.status = 'in-progress'
    db.session.commit()
    
    # Simulate scan progress
    for i in range(10):
        time.sleep(1)
        scan.status = f"in-progress ({i*10}%)"
        db.session.commit()
        
        if i == 9:
            # Generate mock findings
            findings = [
                f"Database '{scan.database_config.name}' found 5 email addresses in plain text",
                f"Database '{scan.database_config.name}' has weak access controls",
                f"Database '{scan.database_config.name}' found 2 personal IDs not masked"
            ]
            
            scan.findings = json.dumps(findings)
            scan.status = 'completed'
            scan.report_file = generate_pdf_report(findings)
            db.session.commit()
            logger.info("Scan completed")
    
    logger.info("Scan simulation finished")

# Database Connection Management
def get_db_connection(config):
    try:
        if config.driver == 'psycopg2':
            import psycopg2
            conn = psycopg2.connect(
                host=config.host,
                port=config.port,
                user=config.username,
                password=config.password,
                database=config.database_name
            )
        elif config.driver == 'mysql.connector':
            import mysql.connector
            conn = mysql.connector.connect(
                host=config.host,
                port=config.port,
                user=config.username,
                password=config.password,
                database=config.database_name
            )
        else:
            raise ValueError(f"Unsupported database driver: {config.driver}")
            
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return None

# Main Application
@app.route('/')
def index():
    # Check if database exists and initialize if needed
    if not os.path.exists('compliance.db'):
        db.create_all()
    
    # Get all database configurations
    configs = DatabaseConfig.query.all()
    
    return render_template('index.html', 
                         configs=configs,
                         compliance_requirements=COMPLIANCE_REQUIREMENTS)

@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        # Create new database configuration
        data = request.form
        new_config = DatabaseConfig(
            name=data['name'],
            host=data['host'],
            port=int(data['port']),
            username=data['username'],
            password=data['password'],
            database_name=data['database_name'],
            driver=data['driver']
        )
        db.session.add(new_config)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Database configuration saved'})
    
    # Get all database configurations
    configs = DatabaseConfig.query.all()
    
    return render_template('config.html', 
                         configs=configs,
                         compliance_requirements=COMPLIANCE_REQUIREMENTS)

@app.route('/scan', methods=['POST'])
def scan():
    config_id = request.form.get('config_id')
    if not config_id:
        return jsonify({'success': False, 'message': 'No configuration selected'})
    
    config = DatabaseConfig.query.get(config_id)
    if not config:
        return jsonify({'success': False, 'message': 'Invalid configuration'})
    
    # Create new scan result
    new_scan = ScanResult(database_config_id=config.id)
    db.session.add(new_scan)
    db.session.commit()
    
    # Start scan in background thread
    thread = threading.Thread(target=scan_worker, args=(new_scan.id,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'scan_id': new_scan.id})

@app.route('/scans', methods=['GET'])
def scans():
    scans_data = ScanResult.query.order_by(ScanResult.scan_date.desc()).all()
    return jsonify({
        'success': True,
        'scans': [{
            'id': s.id,
            'config': s.database_config.name,
            'status': s.status,
            'scan_date': s.scan_date.isoformat() if isinstance(s.scan_date, datetime) else s.scan_date,
            'findings': json.loads(s.findings) if s.findings else None,
            'report': s.report_file
        } for s in scans_data]
    })

@app.route('/download_report/<int:scan_id>')
def download_report(scan_id):
    scan = ScanResult.query.get(scan_id)
    if not scan or not scan.report_file:
        return jsonify({'success': False, 'message': 'Report not found'})
    
    return send_file(scan.report_file, as_attachment=True)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

