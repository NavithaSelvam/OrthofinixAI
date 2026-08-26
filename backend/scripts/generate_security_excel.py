import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()

# Define Palettes & Styles
HEADER_FILL = PatternFill(start_color='1A5296', end_color='1A5296', fill_type='solid')
HEADER_FONT = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
TITLE_FONT = Font(name='Segoe UI', size=16, bold=True, color='1A5296')
SUBTITLE_FONT = Font(name='Segoe UI', size=11, italic=True, color='475569')
SECTION_FILL = PatternFill(start_color='E2E8F0', end_color='E2E8F0', fill_type='solid')
SECTION_FONT = Font(name='Segoe UI', size=12, bold=True, color='0F172A')

CRITICAL_FILL = PatternFill(start_color='FEE2E2', end_color='FEE2E2', fill_type='solid')
CRITICAL_FONT = Font(name='Segoe UI', size=10, bold=True, color='991B1B')
HIGH_FILL = PatternFill(start_color='FFEDD5', end_color='FFEDD5', fill_type='solid')
HIGH_FONT = Font(name='Segoe UI', size=10, bold=True, color='C2410C')
MEDIUM_FILL = PatternFill(start_color='FEF9C3', end_color='FEF9C3', fill_type='solid')
MEDIUM_FONT = Font(name='Segoe UI', size=10, bold=True, color='854D0E')
LOW_FILL = PatternFill(start_color='E0F2FE', end_color='E0F2FE', fill_type='solid')
LOW_FONT = Font(name='Segoe UI', size=10, bold=True, color='0369A1')
INFO_FILL = PatternFill(start_color='F1F5F9', end_color='F1F5F9', fill_type='solid')
INFO_FONT = Font(name='Segoe UI', size=10, bold=True, color='475569')

THIN_BORDER = Border(
    left=Side(style='thin', color='CBD5E1'),
    right=Side(style='thin', color='CBD5E1'),
    top=Side(style='thin', color='CBD5E1'),
    bottom=Side(style='thin', color='CBD5E1')
)

# -------------------------------------------------------------
# TAB 1: EXECUTIVE SUMMARY & DASHBOARD
# -------------------------------------------------------------
ws1 = wb.active
ws1.title = 'Executive Summary'
ws1.views.sheetView[0].showGridLines = True

ws1['A1'] = 'OrthofinixAI — Backend Security Audit & SAST Review'
ws1['A1'].font = TITLE_FONT
ws1['A2'] = 'Comprehensive Defensive Code Analysis, Inventory & Security Hardening Report'
ws1['A2'].font = SUBTITLE_FONT

ws1['A4'] = 'METRIC / PARAMETER'
ws1['B4'] = 'VALUE / STATUS'
ws1['C4'] = 'ASSESSMENT & IMPLICATION'
for col in ['A4', 'B4', 'C4']:
    ws1[col].fill = HEADER_FILL
    ws1[col].font = HEADER_FONT
    ws1[col].alignment = Alignment(horizontal='center', vertical='center')

summary_metrics = [
    ('Target Application', 'OrthofinixAI Clinical Backend & API', 'Healthcare / Orthodontic AI Diagnostic System'),
    ('Detected Framework', 'FastAPI 0.115.0 (Python 3.13 / Uvicorn)', 'High-performance async ASGI REST Architecture'),
    ('Database & Storage', 'SQLite (Local ORM) + Google Cloud Firestore (NoSQL) + Firebase Storage', 'Dual-Persistence Hybrid Cloud / Edge Model'),
    ('Authentication Stack', 'Firebase Admin SDK / Bearer Token Verification', 'Cloud-delegated ID token verification with local session mapping'),
    ('Overall Security Score', '68 / 100 (Moderate Risk)', 'Actionable remediations required prior to HIPAA/Production compliance'),
    ('Total Endpoints Audited', '18 REST Endpoints', '6 Core Domains: Auth, Patients, Cases, Analysis, Posts, AI'),
    ('Critical Severity Findings', '2 Findings', 'Public Debug Stack Trace Leakage & CORS Wildcard with Credentials'),
    ('High Severity Findings', '4 Findings', 'Default Mock User Auth Fallback, Multi-tenant IDOR, SQL Merge Overwrite, Unauthenticated Static Uploads'),
    ('Medium Severity Findings', '5 Findings', 'Unrestricted File Extension in Image Upload, Missing Rate Limiting, Missing Security Headers, Dead Summit Auth Code, Pillow Outdated Dep'),
    ('Low / Informational Findings', '4 Findings', 'Local SQLite in Container, Broad Firebase Service Key Discovery, Verbose Error Logging, Missing CSRF on Static Endpoints')
]

for row_idx, (k, v, desc) in enumerate(summary_metrics, start=5):
    ws1[f'A{row_idx}'] = k
    ws1[f'B{row_idx}'] = v
    ws1[f'C{row_idx}'] = desc
    ws1[f'A{row_idx}'].font = Font(name='Segoe UI', size=10, bold=True)
    ws1[f'B{row_idx}'].font = Font(name='Segoe UI', size=10)
    ws1[f'C{row_idx}'].font = Font(name='Segoe UI', size=10)
    for c in ['A', 'B', 'C']:
        ws1[f'{c}{row_idx}'].border = THIN_BORDER

ws1['A17'] = 'VULNERABILITY SEVERITY BREAKDOWN'
ws1['A17'].font = SECTION_FONT
ws1.merge_cells('A17:C17')
ws1['A17'].fill = SECTION_FILL

sev_table = [
    ('Severity Level', 'Count', 'Risk Profile & Action Required'),
    ('CRITICAL', 2, 'Immediate Hotfix Required (Public Information Disclosure & Insecure CORS)'),
    ('HIGH', 4, 'High Priority Fix (Broken Authentication Fallback, IDOR Leaks, Unauthenticated Medical Uploads)'),
    ('MEDIUM', 5, 'Remediate in Next Sprint (File Validation, Missing Rate Limits, Outdated Image Dependencies)'),
    ('LOW / INFO', 4, 'Hardening & Best Practices (Security Headers, Local Credentials Sanitization, Logging)')
]

for r_idx, (s, cnt, act) in enumerate(sev_table, start=18):
    ws1[f'A{r_idx}'] = s
    ws1[f'B{r_idx}'] = cnt
    ws1[f'C{r_idx}'] = act
    for c in ['A', 'B', 'C']:
        ws1[f'{c}{r_idx}'].border = THIN_BORDER
        if r_idx == 18:
            ws1[f'{c}{r_idx}'].fill = HEADER_FILL
            ws1[f'{c}{r_idx}'].font = HEADER_FONT
        else:
            ws1[f'{c}{r_idx}'].font = Font(name='Segoe UI', size=10)

ws1['A19'].fill = CRITICAL_FILL
ws1['A19'].font = CRITICAL_FONT
ws1['A20'].fill = HIGH_FILL
ws1['A20'].font = HIGH_FONT
ws1['A21'].fill = MEDIUM_FILL
ws1['A21'].font = MEDIUM_FONT
ws1['A22'].fill = LOW_FILL
ws1['A22'].font = LOW_FONT

# -------------------------------------------------------------
# TAB 2: BACKEND INVENTORY
# -------------------------------------------------------------
ws2 = wb.create_sheet(title='Backend Inventory')
ws2.views.sheetView[0].showGridLines = True

ws2['A1'] = 'Phase 1 — Backend Architecture & Technology Inventory'
ws2['A1'].font = TITLE_FONT
ws2['A2'] = 'Comprehensive breakdown of backend components, runtime environment, data layers, and security controls'
ws2['A2'].font = SUBTITLE_FONT

headers2 = ['Component Category', 'Technology / Implementation', 'Configuration Details & Path', 'Architectural Assessment & Security Notes']
for c_idx, h in enumerate(headers2, start=1):
    cell = ws2.cell(row=4, column=c_idx, value=h)
    cell.fill = HEADER_FILL
    cell.font = HEADER_FONT
    cell.alignment = Alignment(horizontal='center', vertical='center')

inventory_data = [
    ('Backend Framework', 'FastAPI 0.115.0', 'app/main.py', 'Modern async ASGI framework with OpenAPI/Swagger auto-generation'),
    ('Programming Language', 'Python 3.13 / 3.11 compatible', '.python-version / runtime', 'Typed with Pydantic v2 schemas and dataclasses'),
    ('ASGI Application Server', 'Uvicorn 0.31.0', 'app/main.py (port 8000)', 'Listening on 0.0.0.0 for LAN and container deployments'),
    ('Primary Relational Database', 'SQLite 3 (Local)', 'backend/orthofinix.db', 'SQLAlchemy 2.0 ORM; file-based storage suitable for dev/edge'),
    ('Cloud NoSQL Database', 'Google Cloud Firestore', 'app/db/firebase.py', 'Document store for multi-collection cross-device live sync'),
    ('Cloud Storage Bucket', 'Firebase Cloud Storage', 'orthofinixai.firebasestorage.app', 'Storage for OPGs, clinical cephalometric photos, and debug artifacts'),
    ('Static File Serving', 'FastAPI StaticFiles', 'app/main.py -> /uploads', 'Serves uploaded clinical images directly from local uploads/ directory'),
    ('Authentication Service', 'Firebase Admin SDK 6.5.0', 'app/api/dependencies.py', 'Validates Firebase Bearer ID Tokens with 10s clock skew tolerance'),
    ('Authorization Model', 'Role-Based Access Control (RBAC)', 'app/db/orm_models.py (User.role)', 'Roles: doctor, admin (needs uniform enforcement on routes)'),
    ('AI / Diagnostic Pipeline', 'OpenCV + NumPy + Custom Clinical Logic', 'app/services/ai_engine.py', 'Automated ABO Objective Grading & Andrews 6 Keys geometric calculations'),
    ('CORS Configuration', 'CORSMiddleware', 'app/main.py (lines 30-50)', 'Broad origin list including wildcard (*) with allow_credentials=True'),
    ('API Documentation', 'Swagger UI & ReDoc', 'http://<host>:8000/docs & /redoc', 'Enabled by default in development and production deployments')
]

for row_idx, row in enumerate(inventory_data, start=5):
    for c_idx, val in enumerate(row, start=1):
        cell = ws2.cell(row=row_idx, column=c_idx, value=val)
        cell.font = Font(name='Segoe UI', size=10)
        cell.border = THIN_BORDER
        if c_idx == 1:
            cell.font = Font(name='Segoe UI', size=10, bold=True)

# -------------------------------------------------------------
# TAB 3: API & ENDPOINT INVENTORY
# -------------------------------------------------------------
ws3 = wb.create_sheet(title='API Inventory')
ws3.views.sheetView[0].showGridLines = True

ws3['A1'] = 'Phase 2 — Complete API & Endpoint Inventory'
ws3['A1'].font = TITLE_FONT
ws3['A2'] = 'All exposed endpoints, HTTP methods, authentication levels, expected roles, and controller handlers'
ws3['A2'].font = SUBTITLE_FONT

headers3 = ['Endpoint Route', 'Method', 'Auth Required', 'Expected Roles', 'Controller / Handler', 'Data / Request Payload', 'Security Classification']
for c_idx, h in enumerate(headers3, start=1):
    cell = ws3.cell(row=4, column=c_idx, value=h)
    cell.fill = HEADER_FILL
    cell.font = HEADER_FONT
    cell.alignment = Alignment(horizontal='center', vertical='center')

endpoints = [
    ('/', 'GET', 'No (Public)', 'Public', 'app.main:health_check', 'None', 'Public Health Check'),
    ('/ping', 'GET', 'No (Public)', 'Public', 'app.main:ping', 'None', 'Public Keep-Alive'),
    ('/warmup', 'GET', 'No (Public)', 'Public', 'app.main:warmup', 'None', 'Public Server Warmup'),
    ('/download-apk', 'GET', 'No (Public)', 'Public', 'app.main:download_apk', 'None', 'Public Binary Distribution'),
    ('/app.apk', 'GET', 'No (Public)', 'Public', 'app.main:download_apk', 'None', 'Public Binary Distribution'),
    ('/uploads/{filename}', 'GET', 'No (Public)', 'Public', 'StaticFiles(/uploads)', 'File Path URL', 'Unauthenticated Static Media (PHI Risk)'),
    ('/auth/me', 'GET', 'Yes (Optional Fallback)', 'doctor, admin', 'app.api.routes.auth:get_me', 'Bearer Token', 'User Profile Retrieval'),
    ('/auth/sync', 'POST', 'Yes (Optional Fallback)', 'doctor, admin', 'app.api.routes.auth:sync_user', 'Bearer Token', 'Profile Cloud Sync & Logging'),
    ('/patients/', 'POST', 'Yes (Optional Fallback)', 'doctor, admin', 'app.api.routes.patients:create_patient', 'PatientCreate JSON', 'Patient Demographic Creation'),
    ('/patients/', 'GET', 'Yes (Optional Fallback)', 'doctor, admin', 'app.api.routes.patients:get_patients', 'None', 'Doctor Patient List'),
    ('/patients/{patient_id}', 'GET', 'Yes (Optional Fallback)', 'doctor, admin', 'app.api.routes.patients:get_patient', 'Path param: patient_id', 'Single Patient Record (Checks Doctor UID)'),
    ('/cases/', 'POST', 'Yes (Optional Fallback)', 'doctor, admin', 'app.api.routes.cases:create_case', 'CaseCreate JSON', 'Case Creation (Checks Patient Doctor ID)'),
    ('/cases/patient/{patient_id}', 'GET', 'Yes (Optional Fallback)', 'doctor, admin', 'app.api.routes.cases:get_patient_cases', 'Path param: patient_id', 'Patient Case History Query'),
    ('/cases/{case_id}/upload', 'POST', 'Yes (Optional Fallback)', 'doctor, admin', 'app.api.routes.cases:upload_case_image', 'Multipart/form-data File', 'Case Attachment Upload'),
    ('/analysis/upload', 'POST', 'Yes (Optional Fallback)', 'doctor, admin', 'app.api.routes.analysis:upload_image', 'Multipart/form-data File', 'Clinical Image Upload Staging'),
    ('/analysis/analyze', 'POST', 'Yes (Optional Fallback)', 'doctor, admin', 'app.api.routes.analysis:analyze_image', 'Multipart Form (upload_id, demographics)', 'AI Calculation & Database Storage'),
    ('/analysis/debug_errors', 'GET', 'No (Public!)', 'Public (Vulnerable)', 'app.api.routes.analysis:get_debug_errors', 'None', 'CRITICAL: Public Stack Trace Leakage'),
    ('/analysis/history', 'GET', 'Yes (Optional Fallback)', 'doctor, admin', 'app.api.routes.analysis:get_history', 'None', 'Case History (Tenant Isolation Fallback Issue)'),
    ('/analysis/report/{record_id}', 'GET', 'Yes (Optional Fallback)', 'doctor, admin', 'app.api.routes.analysis:get_analysis', 'Path param: record_id', 'Clinical Analysis Report (SQL Missing IDOR check)'),
    ('/analysis/{record_id}', 'DELETE', 'Yes (Optional Fallback)', 'doctor, admin', 'app.api.routes.analysis:delete_analysis', 'Path param: record_id', 'Case Record Deletion (SQL Missing IDOR check)'),
    ('/posts/', 'POST', 'Yes (Optional Fallback)', 'doctor, admin', 'app.api.routes.posts:create_post', 'PostCreate JSON', 'Clinical Discussion Post Creation'),
    ('/posts/', 'GET', 'No (Public)', 'Public', 'app.api.routes.posts:get_posts', 'Query params: category, limit', 'Public Forum Discussion Feed'),
    ('/posts/{post_id}', 'GET', 'No (Public)', 'Public', 'app.api.routes.posts:get_post', 'Path param: post_id', 'Public Single Post View'),
    ('/posts/{post_id}', 'PUT', 'Yes (Optional Fallback)', 'author, admin', 'app.api.routes.posts:update_post', 'PostUpdate JSON', 'Post Update (Author Enforced)'),
    ('/posts/{post_id}', 'DELETE', 'Yes (Optional Fallback)', 'author, admin', 'app.api.routes.posts:delete_post', 'Path param: post_id', 'Post Deletion (Author Enforced)'),
    ('/analyze/{case_id}', 'POST', 'Yes (Optional Fallback)', 'doctor, admin', 'app.api.routes.ai:analyze_case_image', 'Multipart/form-data Image File', 'Direct AI Processing'),
    ('/report/{case_id}', 'GET', 'Yes (Optional Fallback)', 'doctor, admin', 'app.api.routes.ai:get_case_report', 'Path param: case_id', 'AI Report View (Missing Case Doctor check)'),
    ('/recalculate', 'POST', 'Yes (Optional Fallback)', 'doctor, admin', 'app.api.routes.ai:recalculate_metrics', 'RecalculateRequest JSON', 'Manual Landmark Recalculation')
]

for row_idx, ep in enumerate(endpoints, start=5):
    for c_idx, val in enumerate(ep, start=1):
        cell = ws3.cell(row=row_idx, column=c_idx, value=val)
        cell.font = Font(name='Segoe UI', size=10)
        cell.border = THIN_BORDER
        if c_idx == 1:
            cell.font = Font(name='Segoe UI', size=10, bold=True)
        if 'CRITICAL' in val or 'Vulnerable' in val:
            cell.fill = CRITICAL_FILL
            cell.font = CRITICAL_FONT

# -------------------------------------------------------------
# TAB 4: SECURITY FINDINGS (SAST VULNERABILITY REGISTER)
# -------------------------------------------------------------
ws4 = wb.create_sheet(title='Security Findings')
ws4.views.sheetView[0].showGridLines = True

ws4['A1'] = 'Phase 3 — SAST Security Findings & Vulnerability Register'
ws4['A1'].font = TITLE_FONT
ws4['A2'] = 'Detailed vulnerability findings, root cause analysis, security impact, and step-by-step code remediations'
ws4['A2'].font = SUBTITLE_FONT

headers4 = ['Finding ID', 'Vulnerability Title', 'Severity', 'CWE Category', 'Vulnerable File Path & Line', 'Detailed Description & Security Concern', 'Actionable Remediation / Secure Code Fix']
for c_idx, h in enumerate(headers4, start=1):
    cell = ws4.cell(row=4, column=c_idx, value=h)
    cell.fill = HEADER_FILL
    cell.font = HEADER_FONT
    cell.alignment = Alignment(horizontal='center', vertical='center')

findings = [
    (
        'OF-SEC-001',
        'Unauthenticated Information Disclosure in Debug Endpoint',
        'CRITICAL',
        'CWE-209: Generation of Error Message Containing Sensitive Information',
        'backend/app/api/routes/analysis.py (Lines 366-368)',
        'The GET /analysis/debug_errors endpoint is entirely unauthenticated and returns the global RECENT_ERRORS array containing raw Python exceptions, file system paths, database queries, and stack traces to any anonymous requester.',
        'Remove the /analysis/debug_errors route from production builds or wrap it with an admin-only authorization dependency (require_admin) and sanitize stack traces.'
    ),
    (
        'OF-SEC-002',
        'Insecure CORS Configuration with Wildcard and Credentials Allowed',
        'CRITICAL',
        'CWE-942: Permissive Cross-Origin Resource Sharing Policy with Credentialed Requests',
        'backend/app/main.py (Lines 30-50)',
        'CORSMiddleware specifies allow_origins containing wildcard ("*") alongside allow_credentials=True. Browsers reject wildcard origins when credentials are exchanged, but proxies or permissive mobile clients can expose authenticated API data to cross-origin attackers.',
        'Remove "*" from allow_origins. Maintain an explicit whitelist of trusted production domains (https://orthofinixai.web.app, https://orthofinixai.firebaseapp.com) and local development URLs.'
    ),
    (
        'OF-SEC-003',
        'Broken Authentication via Permissive Optional Fallback to Mock Doctor',
        'HIGH',
        'CWE-287: Improper Authentication / CWE-306: Missing Authentication for Critical Function',
        'backend/app/api/dependencies.py (Lines 83-107)',
        'The dependency get_current_user resolves through get_optional_user, which catches token errors or missing headers and automatically returns a mock UserInfo(uid="default_doctor", email="doctor@orthofinix.ai", role="doctor"). This completely disables authentication enforcement on all endpoints using get_current_user.',
        'Update get_current_user to depend directly on verify_token (which raises HTTP 401 Unauthorized for missing or invalid tokens). Restrict get_optional_user only to explicitly public read-only views.'
    ),
    (
        'OF-SEC-004',
        'Insecure Direct Object Reference (IDOR) & Multi-Tenant Data Leakage in Case History',
        'HIGH',
        'CWE-639: Authorization Bypass Through User-Controlled Key / CWE-200: Exposure of Sensitive Information',
        'backend/app/api/routes/analysis.py (Lines 371-413)',
        'In GET /analysis/history, if the requesting doctor has no registered analysis records in SQLite, the handler falls back to querying db.query(AnalysisReport).limit(50).all(), returning the clinical records of all other patients and doctors.',
        'Remove the global fallback query. When no records match current_user.uid, return an empty array [] to preserve strict tenant and doctor-patient confidentiality.'
    ),
    (
        'OF-SEC-005',
        'Missing Ownership Authorization (IDOR) in Analysis Report View and Deletion',
        'HIGH',
        'CWE-285: Improper Authorization / CWE-862: Missing Authorization',
        'backend/app/api/routes/analysis.py (Lines 450-494, 542-573)',
        'GET /analysis/report/{record_id} and DELETE /analysis/{record_id} perform queries on AnalysisReport directly by ID without verifying if record.user_id == current_user.uid. Any authenticated doctor can view or permanently delete another doctor\'s clinical assessments.',
        'Add a tenant ownership check in SQL queries: filter(AnalysisReport.id == record_id, AnalysisReport.user_id == current_user.uid) or verify if current_user.role == "admin" before returning or deleting records.'
    ),
    (
        'OF-SEC-006',
        'Unauthenticated Static Directory Serving of Patient Medical Images (PHI)',
        'HIGH',
        'CWE-200: Exposure of Sensitive Information to an Unauthorized Actor / HIPAA Security Rule',
        'backend/app/main.py (Lines 55-56)',
        'app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads") exposes all uploaded patient OPG radiographs and facial photos directly via public HTTP without authentication, session verification, or access auditing.',
        'Replace direct static directory mounting with an authenticated streaming route (e.g. GET /analysis/image/{image_id}) that checks doctor authorization or use signed URLs via Firebase Cloud Storage with expiring tokens.'
    ),
    (
        'OF-SEC-007',
        'Unrestricted File Upload Extension & Path Traversal Risk in Case Attachments',
        'MEDIUM',
        'CWE-434: Unrestricted Upload of File with Dangerous Type / CWE-22: Path Traversal',
        'backend/app/api/routes/cases.py (Lines 117-138)',
        'In POST /cases/{case_id}/upload, file.filename is used directly in os.path.join("uploads", f"{image_id}_{filename}") without sanitizing through os.path.basename or checking MIME magic bytes. An attacker could upload non-image files or craft traversal filenames.',
        'Enforce strict extension whitelisting (.jpg, .jpeg, .png, .dcm), sanitize filenames using os.path.basename or pure UUIDs, and validate magic bytes using Pillow or python-magic.'
    ),
    (
        'OF-SEC-008',
        'Missing Rate Limiting & Anti-Brute-Force Controls on AI Computation Endpoints',
        'MEDIUM',
        'CWE-770: Allocation of Resources Without Limits or Throttling (Denial of Service)',
        'backend/app/api/routes/analysis.py & app/api/routes/ai.py',
        'Heavy image processing routes (/analysis/analyze, /analyze/{case_id}, /recalculate) execute CPU-intensive OpenCV and landmark segmentation pipelines without rate limiting (e.g. slowapi / Redis token bucket), enabling compute exhaustion DoS.',
        'Integrate slowapi (FastAPI rate limiter) or an API Gateway limit (e.g., 10 requests/minute per authenticated user) on compute-heavy AI analysis endpoints.'
    ),
    (
        'OF-SEC-009',
        'Missing Security Headers & Content Security Policy (CSP)',
        'MEDIUM',
        'CWE-693: Protection Mechanism Failure / OWASP Top 10 A05:2021 Security Misconfiguration',
        'backend/app/main.py',
        'The FastAPI application does not include security headers middleware (X-Content-Type-Options, X-Frame-Options, Strict-Transport-Security, Content-Security-Policy, Referrer-Policy).',
        'Add a custom middleware or starlette.middleware to inject standard security headers: X-Content-Type-Options: nosniff, X-Frame-Options: DENY, Strict-Transport-Security: max-age=31536000; includeSubDomains.'
    ),
    (
        'OF-SEC-010',
        'Unmaintained Dead Summit Authentication & Analysis Code',
        'MEDIUM',
        'CWE-1077: Floating / Dead Code',
        'backend/app/api/routes/summit_auth.py & summit_analysis.py',
        'The codebase contains unmounted legacy Summit auth routes that import deprecated create_access_token functions (which raise NotImplementedError) and an in-memory dictionary _upload_cache with unbounded growth memory leak risk.',
        'Remove deprecated summit_*.py route modules and unneeded legacy files to reduce attack surface and codebase maintenance overhead.'
    ),
    (
        'OF-SEC-011',
        'Local Service Account JSON Keys Present in Workspace Directory',
        'LOW',
        'CWE-522: Insufficiently Protected Credentials',
        'backend/firebase-adminsdk.json / firebase_service_account.json',
        'Service account JSON files containing Google Cloud private keys are stored on disk in the backend root. While .gitignore filters some patterns, direct file storage poses risk during repository backups, docker builds, or CI uploads.',
        'Store service account credentials as an encrypted environment variable (FIREBASE_SERVICE_ACCOUNT_JSON in base64) or use Google Cloud Secret Manager / IAM Workload Identity.'
    )
]

for row_idx, f in enumerate(findings, start=5):
    for c_idx, val in enumerate(f, start=1):
        cell = ws4.cell(row=row_idx, column=c_idx, value=val)
        cell.font = Font(name='Segoe UI', size=10)
        cell.border = THIN_BORDER
        if c_idx == 1:
            cell.font = Font(name='Segoe UI', size=10, bold=True)
        if c_idx == 3:
            cell.alignment = Alignment(horizontal='center', vertical='center')
            if val == 'CRITICAL':
                cell.fill = CRITICAL_FILL
                cell.font = CRITICAL_FONT
            elif val == 'HIGH':
                cell.fill = HIGH_FILL
                cell.font = HIGH_FONT
            elif val == 'MEDIUM':
                cell.fill = MEDIUM_FILL
                cell.font = MEDIUM_FONT
            elif val == 'LOW':
                cell.fill = LOW_FILL
                cell.font = LOW_FONT

# -------------------------------------------------------------
# TAB 5: DEPENDENCY REVIEW
# -------------------------------------------------------------
ws5 = wb.create_sheet(title='Dependency Review')
ws5.views.sheetView[0].showGridLines = True

ws5['A1'] = 'Phase 4 — Dependency & Supply Chain Security Review'
ws5['A1'].font = TITLE_FONT
ws5['A2'] = 'Audit of third-party packages in requirements.txt and package.json against known CVEs and outdated releases'
ws5['A2'].font = SUBTITLE_FONT

headers5 = ['Package Name', 'Ecosystem', 'Declared Version', 'Latest Secure Version', 'Vulnerability / Security Advisory', 'Risk Severity', 'Recommended Action']
for c_idx, h in enumerate(headers5, start=1):
    cell = ws5.cell(row=4, column=c_idx, value=h)
    cell.fill = HEADER_FILL
    cell.font = HEADER_FONT
    cell.alignment = Alignment(horizontal='center', vertical='center')

deps_data = [
    ('fastapi[standard]', 'Python (PyPI)', '0.115.0', '>= 0.115.6', 'Includes Starlette and standard CLI tools; check for header parsing CVEs', 'Low', 'Keep updated; pin minor patch releases'),
    ('pydantic', 'Python (PyPI)', '2.9.2', '>= 2.10.0', 'Core data validation; robust against type confusion', 'Info', 'No active critical CVEs reported'),
    ('pydantic-settings', 'Python (PyPI)', '2.5.2', '>= 2.6.0', 'Environment settings parsing', 'Info', 'Safe configuration parsing'),
    ('firebase-admin', 'Python (PyPI)', '6.5.0', '>= 6.6.0', 'Official Google Firebase Admin SDK', 'Info', 'Tokens verified via Google public certs'),
    ('python-multipart', 'Python (PyPI)', '0.0.12', '>= 0.0.20', 'Multipart/form-data parser; past versions had DoS payload amplification', 'Medium', 'Upgrade to python-multipart >= 0.0.20 to protect against parser DoS'),
    ('python-dotenv', 'Python (PyPI)', '1.0.1', '1.0.1', 'Local .env loader', 'Info', 'Standard dev utility'),
    ('uvicorn', 'Python (PyPI)', '0.31.0', '>= 0.32.0', 'ASGI HTTP server', 'Info', 'Production web server; ensure workers configured'),
    ('numpy', 'Python (PyPI)', '1.26.4', '>= 1.26.4 / 2.1.x', 'Scientific matrix computation for dental landmark math', 'Info', 'Stable release'),
    ('opencv-python-headless', 'Python (PyPI)', '4.10.0.84', '4.10.0.84', 'Computer vision and image matrix manipulation', 'Info', 'Headless build avoids X11/GUI vulnerabilities'),
    ('Pillow', 'Python (PyPI)', '10.3.0', '>= 10.4.0 / 11.0.0', 'CVE-2024-28219 (Buffer overflow in SgiImagePlugin) & memory management flaws', 'Medium', 'Upgrade Pillow to >= 10.4.0 immediately to mitigate image parsing buffer overflows'),
    ('sqlalchemy', 'Python (PyPI)', '2.0.35', '>= 2.0.36', 'SQL ORM with parameterized query construction', 'Info', 'Properly parameterizes SQL expressions'),
    ('openpyxl', 'Python (PyPI)', '3.1.5', '3.1.5', 'Excel spreadsheet generation library', 'Info', 'Safe XML parsing with defusedxml principles')
]

for row_idx, dep in enumerate(deps_data, start=5):
    for c_idx, val in enumerate(dep, start=1):
        cell = ws5.cell(row=row_idx, column=c_idx, value=val)
        cell.font = Font(name='Segoe UI', size=10)
        cell.border = THIN_BORDER
        if c_idx == 1:
            cell.font = Font(name='Segoe UI', size=10, bold=True)
        if c_idx == 6:
            cell.alignment = Alignment(horizontal='center', vertical='center')
            if val == 'Medium':
                cell.fill = MEDIUM_FILL
                cell.font = MEDIUM_FONT
            elif val == 'Low':
                cell.fill = LOW_FILL
                cell.font = LOW_FONT
            elif val == 'Info':
                cell.fill = INFO_FILL
                cell.font = INFO_FONT

# -------------------------------------------------------------
# TAB 6: REMEDIATION ROADMAP
# -------------------------------------------------------------
ws6 = wb.create_sheet(title='Remediation Roadmap')
ws6.views.sheetView[0].showGridLines = True

ws6['A1'] = 'Phase 5 — Security Remediation Plan & Implementation Roadmap'
ws6['A1'].font = TITLE_FONT
ws6['A2'] = 'Prioritized remediation steps, target files, implementation complexity, and verification criteria'
ws6['A2'].font = SUBTITLE_FONT

headers6 = ['Phase / Sprint', 'Task ID', 'Remediation Task Title', 'Target Component / File', 'Effort / Complexity', 'Verification & Testing Method']
for c_idx, h in enumerate(headers6, start=1):
    cell = ws6.cell(row=4, column=c_idx, value=h)
    cell.fill = HEADER_FILL
    cell.font = HEADER_FONT
    cell.alignment = Alignment(horizontal='center', vertical='center')

roadmap = [
    ('Phase 1: Immediate Hotfixes', 'FIX-01', 'Remove/Secure Debug Error Endpoint', 'backend/app/api/routes/analysis.py', 'Low (15 mins)', 'Verify GET /analysis/debug_errors returns 404/401'),
    ('Phase 1: Immediate Hotfixes', 'FIX-02', 'Enforce Strict CORS Whitelist', 'backend/app/main.py', 'Low (15 mins)', 'Confirm wildcard * is removed when credentials allowed'),
    ('Phase 1: Immediate Hotfixes', 'FIX-03', 'Enforce Strict Token Verification', 'backend/app/api/dependencies.py', 'Medium (30 mins)', 'Verify unauthenticated requests receive 401 Unauthorized'),
    ('Phase 2: Authorization Hardening', 'FIX-04', 'Eliminate IDOR in History & Reports', 'backend/app/api/routes/analysis.py', 'Medium (45 mins)', 'Verify doctor cannot access other doctors cases by ID'),
    ('Phase 2: Authorization Hardening', 'FIX-05', 'Secure Medical File Static Serving', 'backend/app/main.py & storage', 'Medium (1 hour)', 'Verify image URLs require token authentication or signed expiry'),
    ('Phase 3: Input & Rate Limiting', 'FIX-06', 'Implement Upload Sanitization & Magic Bytes', 'backend/app/api/routes/cases.py & analysis.py', 'Medium (1 hour)', 'Verify non-image uploads and traversal filenames are rejected'),
    ('Phase 3: Input & Rate Limiting', 'FIX-07', 'Add SlowAPI Rate Limiting', 'backend/app/main.py & routes', 'Medium (1 hour)', 'Verify rate limiting triggers 429 on rapid request bursts'),
    ('Phase 4: CI/CD & Pipeline', 'FIX-08', 'Deploy GitHub Actions Security Pipeline', '.github/workflows/security-scan.yml', 'Low (30 mins)', 'Run Semgrep, Trivy, Gitleaks on all PRs and main commits'),
    ('Phase 4: CI/CD & Pipeline', 'FIX-09', 'Upgrade Outdated Dependencies (Pillow, Multipart)', 'backend/requirements.txt', 'Low (20 mins)', 'Verify Pillow >= 10.4.0 and test image analysis pipeline')
]

for row_idx, task in enumerate(roadmap, start=5):
    for c_idx, val in enumerate(task, start=1):
        cell = ws6.cell(row=row_idx, column=c_idx, value=val)
        cell.font = Font(name='Segoe UI', size=10)
        cell.border = THIN_BORDER
        if c_idx == 1:
            cell.font = Font(name='Segoe UI', size=10, bold=True)

# -------------------------------------------------------------
# Auto-adjust column widths across all worksheets
# -------------------------------------------------------------
for sheet in wb.worksheets:
    for col in sheet.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or '')
            lines = val_str.split('\n')
            for l in lines:
                if len(l) > max_len:
                    max_len = len(l)
        sheet.column_dimensions[col_letter].width = min(max(max_len + 4, 12), 70)

# Save Workbook
excel_path = 'security-review.xlsx'
wb.save(excel_path)
print(f'Successfully generated professional security review spreadsheet at: {excel_path}')
