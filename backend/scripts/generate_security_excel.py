import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def create_security_excel():
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    # Styles
    navy_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    header_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    blue_header_fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
    
    crit_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
    crit_font = Font(name="Calibri", size=11, bold=True, color="991B1B")
    
    high_fill = PatternFill(start_color="FFEDD5", end_color="FFEDD5", fill_type="solid")
    high_font = Font(name="Calibri", size=11, bold=True, color="9A3412")
    
    med_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
    med_font = Font(name="Calibri", size=11, bold=True, color="92400E")
    
    low_fill = PatternFill(start_color="E0F2FE", end_color="E0F2FE", fill_type="solid")
    low_font = Font(name="Calibri", size=11, bold=True, color="075985")
    
    white_bold = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    title_font = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
    subtitle_font = Font(name="Calibri", size=12, italic=True, color="94A3B8")
    bold_font = Font(name="Calibri", size=11, bold=True, color="0F172A")
    regular_font = Font(name="Calibri", size=11, color="1E293B")
    
    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    # ==========================================
    # SHEET 1: Executive Summary
    # ==========================================
    ws_exec = wb.create_sheet(title="Executive Summary")
    ws_exec.views.sheetView[0].showGridLines = True
    
    # Title Block
    ws_exec.merge_cells("A1:G2")
    top_cell = ws_exec["A1"]
    top_cell.value = "OrthofinixAI — Comprehensive Backend Security Audit Report"
    top_cell.font = title_font
    top_cell.fill = header_fill
    top_cell.alignment = Alignment(horizontal="center", vertical="center")
    
    ws_exec["A3"] = "Target Repository:"
    ws_exec["B3"] = "OrthofinixAI (FastAPI + SQLite/Firestore + ONNX Engine)"
    ws_exec["A4"] = "Assessment Type:"
    ws_exec["B4"] = "Defensive Static Application Security Testing (SAST) & Architecture Audit"
    ws_exec["A5"] = "Review Date:"
    ws_exec["B5"] = "August 2026"
    ws_exec["A6"] = "Overall Security Score:"
    ws_exec["B6"] = "76 / 100 (Grade: B - Remediations Required)"
    
    for row in range(3, 7):
        ws_exec[f"A{row}"].font = bold_font
        ws_exec[f"B{row}"].font = regular_font
        ws_exec[f"A{row}"].fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")

    # Scorecard Table
    ws_exec["A8"] = "Metric"
    ws_exec["B8"] = "Value / Status"
    ws_exec["C8"] = "Benchmark / Target"
    for col in ["A", "B", "C"]:
        cell = ws_exec[f"{col}8"]
        cell.font = white_bold
        cell.fill = blue_header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    metrics_data = [
        ("Total API Endpoints Audited", "24 Endpoints", "100% Coverage"),
        ("Critical Vulnerabilities (CVSS 9.0 - 10.0)", "1 Finding", "0 Required"),
        ("High Severity Vulnerabilities (CVSS 7.0 - 8.9)", "3 Findings", "0 Required"),
        ("Medium Severity Weaknesses (CVSS 4.0 - 6.9)", "3 Findings", "< 2 Target"),
        ("Low Severity / Informational (CVSS 0.1 - 3.9)", "2 Findings", "< 5 Target"),
        ("Authentication Standard", "Firebase Auth Bearer ID Tokens", "Compliant"),
        ("Database Security", "SQLAlchemy Parameterized Queries (Zero SQLi)", "Compliant"),
        ("Broken Object Level Auth (IDOR)", "2 Endpoints Vulnerable (/analysis/{id}, /patients/{id})", "Remediation Immediate"),
    ]

    for idx, (m, v, b) in enumerate(metrics_data, start=9):
        ws_exec[f"A{idx}"] = m
        ws_exec[f"B{idx}"] = v
        ws_exec[f"C{idx}"] = b
        ws_exec[f"A{idx}"].font = regular_font
        ws_exec[f"B{idx}"].font = bold_font
        ws_exec[f"C{idx}"].font = regular_font
        for col in ["A", "B", "C"]:
            ws_exec[f"{col}{idx}"].border = thin_border

    # ==========================================
    # SHEET 2: Backend Inventory
    # ==========================================
    ws_inv = wb.create_sheet(title="Backend Inventory")
    ws_inv.views.sheetView[0].showGridLines = True
    
    headers_inv = ["Architectural Component", "Detected Technology", "Configuration / Implementation Details", "Security Impact / Evaluation"]
    for col_idx, h in enumerate(headers_inv, start=1):
        cell = ws_inv.cell(row=1, column=col_idx, value=h)
        cell.font = white_bold
        cell.fill = blue_header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    inv_rows = [
        ("Core Backend Framework", "FastAPI (v0.115.0) + Starlette", "Asynchronous ASGI web application running on Python 3.10+", "Modern, high performance; requires explicit middleware for security headers."),
        ("ASGI Web Server", "Uvicorn (v0.31.0)", "Configured with host 0.0.0.0, dynamic port binding", "Production-ready; ensure workers/timeouts are tuned behind reverse proxy."),
        ("Primary Database (RDBMS)", "SQLite (orthofinix_summit.db)", "SQLAlchemy 2.0.35 ORM with declarative models", "Protected against SQL injection via parameterized queries. File-based concurrency limits."),
        ("Cloud NoSQL Store", "Google Cloud Firestore", "Multi-platform sync with Android and React Web", "Requires strict Firestore Rules enforcement to prevent unauthorized client-side tampering."),
        ("File & Object Storage", "Local Static Serving (/uploads) + Firebase Storage", "FastAPI StaticFiles mount + Firebase Cloud Storage buckets", "Static files publicly accessible without per-user auth token checking."),
        ("Authentication Engine", "Firebase Authentication (ID Tokens)", "Bearer token validation via firebase_admin.auth.verify_id_token()", "Industry standard asymmetric JWT verification. Clock skew tolerance set to 10s."),
        ("Authorization Model", "Role-Based (Doctor, Admin) + UID Isolation", "Custom dependency verify_token() mapping to UserInfo schema", "Partial IDOR vulnerabilities identified in delete_patient and delete_analysis endpoints."),
        ("AI / Computer Vision Engine", "ONNX Runtime (1.19.2) + OpenCV + Pillow", "YOLO segmentation, landmark regression, geometric analysis", "Runs in-process. Requires file-size limits to avoid memory exhaustion (DoS)."),
        ("API Documentation", "OpenAPI (Swagger UI) + ReDoc", "Mounted at /docs, /redoc, and /openapi.json", "Exposed in production unless disabled via settings.ENVIRONMENT == 'production'."),
        ("CORS Middleware", "FastAPI CORSMiddleware", "Configured in main.py with wildcard '*' and allow_credentials=True", "High risk: combining wildcard origin with credential allowance violates browser CORS safety."),
    ]

    for r_idx, row in enumerate(inv_rows, start=2):
        for c_idx, val in enumerate(row, start=1):
            cell = ws_inv.cell(row=r_idx, column=c_idx, value=val)
            cell.font = regular_font
            cell.border = thin_border
            cell.alignment = Alignment(wrap_text=True, vertical="top")

    # ==========================================
    # SHEET 3: API Endpoint Inventory
    # ==========================================
    ws_api = wb.create_sheet(title="API Inventory")
    ws_api.views.sheetView[0].showGridLines = True
    
    headers_api = ["Module / Tag", "HTTP Method", "Endpoint Path", "Authentication Required", "Expected Roles", "Controller / Source File", "Security Status"]
    for col_idx, h in enumerate(headers_api, start=1):
        cell = ws_api.cell(row=1, column=col_idx, value=h)
        cell.font = white_bold
        cell.fill = blue_header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    api_rows = [
        ("Auth", "GET", "/auth/me", "Yes (Bearer Token)", "Doctor, Admin", "backend/app/api/routes/auth.py", "Secure"),
        ("Auth", "POST", "/auth/sync", "Yes (Bearer Token)", "Doctor, Admin", "backend/app/api/routes/auth.py", "Secure"),
        ("Patients", "POST", "/patients/", "Yes (Bearer Token)", "Doctor, Admin", "backend/app/api/routes/patients.py", "Secure"),
        ("Patients", "GET", "/patients/", "Yes (Bearer Token)", "Doctor, Admin", "backend/app/api/routes/patients.py", "Secure (UID Filtered)"),
        ("Patients", "GET", "/patients/{patient_id}", "Yes (Bearer Token)", "Doctor, Admin", "backend/app/api/routes/patients.py", "Secure (Doctor ID Verified)"),
        ("Patients", "DELETE", "/patients/{patient_id}", "Yes (Bearer Token)", "Doctor, Admin", "backend/app/api/routes/patients.py", "Vulnerable (BOLA / IDOR)"),
        ("Cases", "POST", "/cases/", "Yes (Bearer Token)", "Doctor, Admin", "backend/app/api/routes/cases.py", "Secure (Patient Ownership Checked)"),
        ("Cases", "GET", "/cases/", "Yes (Bearer Token)", "Doctor, Admin", "backend/app/api/routes/cases.py", "Secure (UID Filtered)"),
        ("Cases", "GET", "/cases/patient/{patient_id}", "Yes (Bearer Token)", "Doctor, Admin", "backend/app/api/routes/cases.py", "Secure"),
        ("Cases", "POST", "/cases/{case_id}/upload", "Yes (Bearer Token)", "Doctor, Admin", "backend/app/api/routes/cases.py", "Medium (MIME validation only)"),
        ("Cases", "DELETE", "/cases/{case_id}", "Yes (Bearer Token)", "Doctor, Admin", "backend/app/api/routes/cases.py", "Vulnerable (Delegates to delete_analysis)"),
        ("Analysis", "POST", "/analysis/upload", "Yes (Bearer Token)", "Doctor, Admin", "backend/app/api/routes/analysis.py", "Medium (MIME validation only)"),
        ("Analysis", "POST", "/analysis/analyze", "Yes (Bearer Token)", "Doctor, Admin", "backend/app/api/routes/analysis.py", "Secure"),
        ("Analysis", "GET", "/analysis/history", "Yes (Bearer Token)", "Doctor, Admin", "backend/app/api/routes/analysis.py", "Secure (UID Filtered)"),
        ("Analysis", "GET", "/analysis/report/{record_id}", "Yes (Bearer Token)", "Doctor, Admin", "backend/app/api/routes/analysis.py", "Secure (Owner / Admin Checked)"),
        ("Analysis", "GET", "/analysis/demo", "No (Public Demo)", "Any", "backend/app/api/routes/analysis.py", "Info (Static Demo Payload)"),
        ("Analysis", "GET", "/analysis/benchmark", "No (Public Benchmark)", "Any", "backend/app/api/routes/analysis.py", "Info (Clinical Benchmark Data)"),
        ("Analysis", "GET", "/analysis/debug_errors", "No (Unauthenticated)", "None", "backend/app/api/routes/analysis.py", "Vulnerable (Info Disclosure)"),
        ("Analysis", "DELETE", "/analysis/{record_id}", "Yes (Bearer Token)", "Doctor, Admin", "backend/app/api/routes/analysis.py", "Critical (Wildcard Match IDOR)"),
        ("Analysis", "POST", "/analysis/delete/{record_id}", "Yes (Bearer Token)", "Doctor, Admin", "backend/app/api/routes/analysis.py", "Critical (Wildcard Match IDOR)"),
        ("Posts", "POST", "/posts/", "Yes (Bearer Token)", "Doctor, Admin", "backend/app/api/routes/posts.py", "Secure"),
        ("Posts", "GET", "/posts/", "No (Public Feed)", "Any", "backend/app/api/routes/posts.py", "Low (Unrestricted Limit)"),
        ("Posts", "GET", "/posts/{post_id}", "No (Public Feed)", "Any", "backend/app/api/routes/posts.py", "Secure"),
        ("Posts", "PUT", "/posts/{post_id}", "Yes (Bearer Token)", "Author, Admin", "backend/app/api/routes/posts.py", "Secure (Author Verified)"),
        ("Posts", "DELETE", "/posts/{post_id}", "Yes (Bearer Token)", "Author, Admin", "backend/app/api/routes/posts.py", "Secure (Author Verified)"),
        ("System", "GET", "/", "No", "Any", "backend/app/main.py", "Secure (Health Check)"),
        ("System", "GET", "/ping", "No", "Any", "backend/app/main.py", "Secure"),
        ("System", "GET", "/warmup", "No", "Any", "backend/app/main.py", "Secure"),
    ]

    for r_idx, row in enumerate(api_rows, start=2):
        for c_idx, val in enumerate(row, start=1):
            cell = ws_api.cell(row=r_idx, column=c_idx, value=val)
            cell.font = regular_font
            cell.border = thin_border
            if c_idx == 7:
                if "Critical" in val:
                    cell.fill = crit_fill
                    cell.font = crit_font
                elif "Vulnerable" in val:
                    cell.fill = high_fill
                    cell.font = high_font
                elif "Medium" in val:
                    cell.fill = med_fill
                    cell.font = med_font
                elif "Secure" in val:
                    cell.font = Font(name="Calibri", size=11, bold=True, color="166534")

    # ==========================================
    # SHEET 4: SAST Security Findings
    # ==========================================
    ws_find = wb.create_sheet(title="Security Findings (SAST)")
    ws_find.views.sheetView[0].showGridLines = True
    
    headers_find = ["Finding ID", "Severity", "OWASP Category", "File Path & Lines", "Vulnerability Description", "Security Impact", "Recommended Remediation"]
    for col_idx, h in enumerate(headers_find, start=1):
        cell = ws_find.cell(row=1, column=col_idx, value=h)
        cell.font = white_bold
        cell.fill = blue_header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    findings = [
        (
            "SEC-01",
            "CRITICAL",
            "A01:2021-Broken Access Control / Insecure Logic",
            "backend/app/api/routes/analysis.py (Lines 1056-1096)",
            "Wildcard Patient Name Deletion & Cross-Doctor Record Purge in delete_analysis endpoint. Using `.ilike(f'%{record_id}%')` allows short strings (e.g., 'a') to match and delete arbitrary patients/reports.",
            "Complete data loss across all doctor accounts. Any user can trigger mass deletion of patient histories and orthodontic diagnostic reports.",
            "Remove `.ilike()` fuzzy matching. Enforce strict UUID equality (`id == record_id`), and require `user_id == current_user.uid` across all SQL/Firestore delete operations."
        ),
        (
            "SEC-02",
            "HIGH",
            "A01:2021-Broken Object Level Authorization (IDOR)",
            "backend/app/api/routes/patients.py (Lines 208-216)",
            "Missing Ownership Check in delete_patient endpoint. The SQL cascade delete executes `Case.patient_id == patient_id` and `Patient.id == patient_id` without verifying `doctor_id == current_user.uid`.",
            "Any authenticated doctor can delete any other doctor's patient records and associated orthodontic case data by supplying their UUID.",
            "Verify patient ownership before executing deletion: `if patient.doctor_id != current_user.uid and current_user.role != 'admin': raise HTTPException(403)`."
        ),
        (
            "SEC-03",
            "HIGH",
            "A05:2021-Security Misconfiguration / Info Disclosure",
            "backend/app/api/routes/analysis.py (Lines 573-575)",
            "Unauthenticated Debug Error Endpoint (`GET /analysis/debug_errors`) returns global in-memory `RECENT_ERRORS` array containing raw exception stack traces, database schema details, and file paths.",
            "Attackers can harvest internal system traces, module paths, and database query failure details without authentication.",
            "Remove `/analysis/debug_errors` from production builds or guard with admin role authentication (`Depends(get_current_user)` and `role == 'admin'`)."
        ),
        (
            "SEC-04",
            "HIGH",
            "A05:2021-Security Misconfiguration / Insecure CORS",
            "backend/app/main.py (Lines 30-50)",
            "CORS configuration combines `allow_origins=['*']` with `allow_credentials=True`. This is unsafe and causes browser security issues.",
            "Allows any arbitrary third-party web domain to issue authenticated cross-origin requests to the backend API.",
            "Remove `'*'` from `allow_origins`. Explicitly whitelist production and staging domains via environment variable `CORS_ORIGINS`."
        ),
        (
            "SEC-05",
            "MEDIUM",
            "A04:2021-Insecure Design / Sensitive File Exposure",
            ".gitignore (Root & Backend)",
            "Incomplete .gitignore rules. While `firebase-adminsdk.json` is ignored, double-extension variants like `firebase-adminsdk.json.json` and `backend/.env` are not explicitly covered.",
            "Risk of accidental repository commits exposing Google Cloud service account private keys and database credentials.",
            "Add `*adminsdk*.json*`, `*.env*`, and `!*.env.example` to root and backend `.gitignore` files."
        ),
        (
            "SEC-06",
            "MEDIUM",
            "A04:2021-Insecure Design / Unrestricted Uploads",
            "backend/app/api/routes/cases.py & analysis.py",
            "File uploads rely exclusively on client-supplied `content_type` header (e.g. `file.content_type.startswith('image/')`) without validating magic file headers (JPEG/PNG bytes).",
            "Attackers could upload arbitrary non-image binaries or oversized files to fill server disk storage.",
            "Inspect first bytes of file buffer using Pillow/OpenCV image verification and enforce maximum file size limit (e.g., 25MB)."
        ),
        (
            "SEC-07",
            "MEDIUM",
            "A05:2021-Security Misconfiguration / Dead Code",
            "backend/app/api/routes/summit_auth.py",
            "Deprecated local authentication endpoints still exposed. Invoking `/register` or `/login` calls `hash_password` which throws unhandled `NotImplementedError` 500.",
            "Generates 500 internal server errors and creates confusion for API consumers.",
            "Deprecate or remove `summit_auth.py` and `summit_analysis.py` routes, routing all authentication through `/auth/me` and Firebase Auth."
        ),
        (
            "SEC-08",
            "LOW",
            "A05:2021-Security Misconfiguration / Missing Headers",
            "backend/app/main.py",
            "Missing HTTP Security Headers middleware. Responses lack `X-Content-Type-Options`, `X-Frame-Options`, and `Content-Security-Policy`.",
            "Client browsers are vulnerable to MIME-sniffing and clickjacking attacks.",
            "Implement a FastAPI middleware to append `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, and `Strict-Transport-Security` to all responses."
        ),
        (
            "SEC-09",
            "LOW",
            "A04:2021-Insecure Design / Rate Limiting",
            "backend/app/api/routes/posts.py",
            "Unrestricted query pagination and lack of rate limiting on public feed (`GET /posts`).",
            "Potential resource exhaustion / DoS if large volumes of requests are sent to scrape the feed.",
            "Enforce strict `max_limit=100` and integrate SlowAPI or Redis rate limiting on public endpoints."
        ),
    ]

    for r_idx, (fid, sev, cat, fpath, desc, imp, rem) in enumerate(findings, start=2):
        row_vals = [fid, sev, cat, fpath, desc, imp, rem]
        for c_idx, val in enumerate(row_vals, start=1):
            cell = ws_find.cell(row=r_idx, column=c_idx, value=val)
            cell.font = regular_font
            cell.border = thin_border
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            if c_idx == 2:
                if sev == "CRITICAL":
                    cell.fill = crit_fill
                    cell.font = crit_font
                elif sev == "HIGH":
                    cell.fill = high_fill
                    cell.font = high_font
                elif sev == "MEDIUM":
                    cell.fill = med_fill
                    cell.font = med_font
                elif sev == "LOW":
                    cell.fill = low_fill
                    cell.font = low_font

    # ==========================================
    # SHEET 5: Dependency Audit
    # ==========================================
    ws_dep = wb.create_sheet(title="Dependency Audit")
    ws_dep.views.sheetView[0].showGridLines = True
    
    headers_dep = ["Package Name", "Current Version", "Latest Secure Version", "Vulnerability / Advisory Reference", "Severity", "Recommended Action"]
    for col_idx, h in enumerate(headers_dep, start=1):
        cell = ws_dep.cell(row=1, column=col_idx, value=h)
        cell.font = white_bold
        cell.fill = blue_header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    dep_rows = [
        ("Pillow", "10.3.0", "10.4.0+ / 11.0.0", "CVE-2024-28219 (Buffer overflow in ImageDraw.floodfill)", "HIGH", "Upgrade to Pillow>=10.4.0 in requirements.txt"),
        ("fastapi", "0.115.0", "0.115.6+", "Stable upstream patches and security fixes", "INFO", "Keep updated with latest minor releases"),
        ("pydantic", "2.9.2", "2.10.4+", "Core validation library update", "INFO", "Compatible with pydantic-settings 2.7+"),
        ("firebase-admin", "6.5.0", "6.6.0+", "Google Cloud authentication and Firestore SDK", "INFO", "Current version stable; upgrade to 6.6.0+"),
        ("python-multipart", "0.0.12", "0.0.20+", "Streaming multipart/form-data parser (DoS mitigation)", "MEDIUM", "Upgrade to python-multipart>=0.0.20"),
        ("sqlalchemy", "2.0.35", "2.0.36+", "SQLAlchemy 2.0 ORM core", "INFO", "Safe against SQL injection via ORM queries"),
        ("onnxruntime", "1.19.2", "1.20.1+", "Machine Learning inference runtime for ONNX models", "INFO", "Safe for verified local clinical model weights"),
        ("opencv-python-headless", "4.10.0.84", "4.10.0.84", "Computer vision image transformation library", "INFO", "Headless version minimizes attack surface"),
    ]

    for r_idx, row in enumerate(dep_rows, start=2):
        for c_idx, val in enumerate(row, start=1):
            cell = ws_dep.cell(row=r_idx, column=c_idx, value=val)
            cell.font = regular_font
            cell.border = thin_border
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            if c_idx == 5:
                if val == "HIGH":
                    cell.fill = high_fill
                    cell.font = high_font
                elif val == "MEDIUM":
                    cell.fill = med_fill
                    cell.font = med_font
                elif val == "INFO":
                    cell.fill = low_fill
                    cell.font = low_font

    # ==========================================
    # SHEET 6: Remediation Roadmap
    # ==========================================
    ws_road = wb.create_sheet(title="Remediation Roadmap")
    ws_road.views.sheetView[0].showGridLines = True
    
    headers_road = ["Priority Phase", "Finding Reference", "Remediation Task", "Effort", "Verification Method"]
    for col_idx, h in enumerate(headers_road, start=1):
        cell = ws_road.cell(row=1, column=col_idx, value=h)
        cell.font = white_bold
        cell.fill = blue_header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    road_rows = [
        ("Phase 1: Immediate (Day 1)", "SEC-01 & SEC-02", "Fix IDOR in delete_analysis and delete_patient endpoints. Strip fuzzy ilike() matching and enforce doctor_id checks.", "2 Hours", "Unit test cross-doctor deletion rejection with 403 Forbidden"),
        ("Phase 1: Immediate (Day 1)", "SEC-03", "Delete or restrict /analysis/debug_errors endpoint to prevent stack trace leaks.", "30 Mins", "Verify endpoint returns 404 or 401 unauthenticated"),
        ("Phase 2: High Priority (Week 1)", "SEC-04", "Sanitize CORS configuration in main.py. Remove '*' wildcard and configure explicit allowed origins list.", "1 Hour", "Test unauthorized origin rejection in browser headers"),
        ("Phase 2: High Priority (Week 1)", "SEC-05", "Update .gitignore to comprehensively block double extensions and local environment files.", "30 Mins", "Run git status to verify no credentials tracked"),
        ("Phase 3: Medium Priority (Week 2)", "SEC-06", "Implement magic-byte image validation for file uploads and enforce 25MB upload limits.", "3 Hours", "Submit test non-image file and confirm 400 rejection"),
        ("Phase 3: Medium Priority (Week 2)", "Dependency Audit", "Update Pillow to >=10.4.0 and python-multipart to >=0.0.20 in requirements.txt.", "1 Hour", "Run pip audit / trivy fs to confirm zero known CVEs"),
        ("Phase 4: Low Priority (Month 1)", "SEC-08 & SEC-09", "Add HTTP Security Headers middleware (CSP, HSTS, X-Frame-Options) and query rate limiting.", "4 Hours", "Verify headers via curl -I https://backend-domain/"),
    ]

    for r_idx, row in enumerate(road_rows, start=2):
        for c_idx, val in enumerate(row, start=1):
            cell = ws_road.cell(row=r_idx, column=c_idx, value=val)
            cell.font = regular_font
            cell.border = thin_border
            cell.alignment = Alignment(wrap_text=True, vertical="top")

    # Set Column Widths for all sheets
    for sheet in wb.worksheets:
        for col in sheet.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or "")
                if len(val_str) > max_len and "\n" not in val_str:
                    max_len = len(val_str)
            sheet.column_dimensions[col_letter].width = min(max(max_len + 4, 12), 48)

    # Specific tweaks
    ws_find.column_dimensions["E"].width = 45
    ws_find.column_dimensions["F"].width = 40
    ws_find.column_dimensions["G"].width = 45
    ws_api.column_dimensions["C"].width = 35
    ws_api.column_dimensions["F"].width = 40
    ws_inv.column_dimensions["C"].width = 45
    ws_inv.column_dimensions["D"].width = 45

    # Save files
    out_root = os.path.abspath("security-review.xlsx")
    out_backend = os.path.abspath(os.path.join("backend", "security-review.xlsx"))
    
    wb.save(out_root)
    wb.save(out_backend)
    print(f"Security Review Excel successfully generated at:\n  - {out_root}\n  - {out_backend}")

if __name__ == "__main__":
    create_security_excel()
