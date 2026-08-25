import { AnalysisReport } from './api';

export function generateAndPrintPDF(report: AnalysisReport) {
  // Retrieve DOB and Gender if cached locally
  const cachedPatientData = localStorage.getItem(`patient_${report.id}`) || localStorage.getItem(`patient_${report.case_id}`);
  let dob = 'N/A';
  let gender = 'N/A';
  if (cachedPatientData) {
    try {
      const parsed = JSON.parse(cachedPatientData);
      dob = parsed.dob || dob;
      gender = parsed.gender || gender;
    } catch (_) {}
  }

  const overallScore = report.finishing_score || 0;
  const statusLabel = overallScore > 80 ? "PROCEED TO DEBOND" : "ADDITIONAL DETAILING REQUIRED";
  const dateStr = report.created_at ? new Date(report.created_at).toLocaleString() : new Date().toLocaleString();

  const printWindow = window.open('', '_blank');
  if (!printWindow) {
    alert('Please allow popups to generate print reports.');
    return;
  }

  const printHtml = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>OrthofinixAI Clinical Report - ${report.patient_name}</title>
      <style>
        body {
          font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
          color: #1e293b;
          margin: 0;
          padding: 40px;
          line-height: 1.5;
        }
        .header {
          background-color: #0c1b33;
          color: white;
          padding: 24px;
          border-radius: 8px;
          margin-bottom: 30px;
        }
        .header h1 {
          margin: 0;
          font-size: 24px;
          letter-spacing: 1px;
        }
        .header p {
          margin: 4px 0 0 0;
          font-size: 12px;
          color: #94a3b8;
        }
        .section-title {
          background-color: #f1f5f9;
          color: #0c1b33;
          font-size: 14px;
          font-weight: bold;
          padding: 8px 12px;
          margin-top: 24px;
          margin-bottom: 12px;
          text-transform: uppercase;
          border-radius: 4px;
        }
        .grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
          font-size: 12px;
          margin-bottom: 20px;
        }
        .grid-item {
          display: flex;
          border-bottom: 1px solid #f1f5f9;
          padding: 4px 0;
        }
        .grid-label {
          font-weight: bold;
          width: 180px;
          color: #0c1b33;
        }
        .grid-value {
          color: #334155;
        }
        .recommendation-list {
          font-size: 12px;
          padding-left: 20px;
          margin: 8px 0;
        }
        .recommendation-item {
          margin-bottom: 6px;
        }
        .score-box {
          border: 2px solid #0c1b33;
          border-radius: 8px;
          padding: 16px;
          text-align: center;
          margin-top: 30px;
        }
        .score-val {
          font-size: 48px;
          font-weight: 900;
          color: #0c1b33;
          margin: 0;
        }
        .score-label {
          font-size: 11px;
          font-weight: bold;
          color: #64748b;
          text-transform: uppercase;
          letter-spacing: 1px;
        }
        .score-status {
          margin-top: 8px;
          font-size: 12px;
          font-weight: bold;
          color: ${overallScore > 80 ? '#76B82A' : '#EF4444'};
        }
        .footer {
          margin-top: 50px;
          font-size: 10px;
          color: #94a3b8;
          text-align: center;
          border-top: 1px solid #e2e8f0;
          padding-top: 15px;
        }
        @media print {
          body {
            padding: 20px;
          }
          .no-print {
            display: none;
          }
        }
      </style>
    </head>
    <body>
      <div class="no-print" style="margin-bottom: 20px; display: flex; gap: 10px;">
        <button onclick="window.print()" style="background-color: #1a5296; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer;">Print / Save as PDF</button>
        <button onclick="window.close()" style="background-color: #e2e8f0; color: #334155; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer;">Close Window</button>
      </div>

      <div class="header">
        <h1>ORTHOFINIX AI CLINICAL REPORT</h1>
        <p>Generated: ${dateStr} | View Type: ${report.view_type?.toUpperCase()}</p>
        <p>Patient Name: ${report.patient_name} | Case ID: ${report.case_id || report.id}</p>
      </div>

      <div class="section-title">Patient Details</div>
      <div class="grid">
        <div class="grid-item"><div class="grid-label">Patient Name:</div><div class="grid-value">${report.patient_name}</div></div>
        <div class="grid-item"><div class="grid-label">Patient Case ID:</div><div class="grid-value">${report.case_id || report.id}</div></div>
        <div class="grid-item"><div class="grid-label">Date of Birth:</div><div class="grid-value">${dob}</div></div>
        <div class="grid-item"><div class="grid-label">Gender:</div><div class="grid-value">${gender}</div></div>
      </div>

      <div class="section-title">Clinical Evaluation</div>
      <div class="grid">
        <div class="grid-item"><div class="grid-label">Overall Confidence Score:</div><div class="grid-value">${Math.round(report.confidence_score * 100)}%</div></div>
        <div class="grid-item"><div class="grid-label">ABO OGS Score:</div><div class="grid-value">${report.abo_score?.toFixed(1) ?? 'N/A'} / 100</div></div>
        <div class="grid-item"><div class="grid-label">Andrews Six Keys Score:</div><div class="grid-value">${report.andrews_score?.toFixed(1) ?? 'N/A'} / 100</div></div>
        <div class="grid-item"><div class="grid-label">Arch Symmetry Score:</div><div class="grid-value">${report.alignment_score?.toFixed(1) ?? 'N/A'}%</div></div>
        <div class="grid-item"><div class="grid-label">Root Angulation Score:</div><div class="grid-value">${report.root_angulation_score?.toFixed(1) ?? 'N/A'}%</div></div>
        <div class="grid-item"><div class="grid-label">Image URL:</div><div class="grid-value" style="word-break: break-all;"><a href="${report.image_url}" target="_blank">${report.image_url || 'N/A'}</a></div></div>
      </div>

      <div class="section-title">Measurements</div>
      <div class="grid">
        <div class="grid-item"><div class="grid-label">Overjet:</div><div class="grid-value">${report.overjet_mm?.toFixed(1) ?? 'N/A'} mm</div></div>
        <div class="grid-item"><div class="grid-label">Overbite:</div><div class="grid-value">${report.overbite_percent?.toFixed(0) ?? 'N/A'}%</div></div>
        <div class="grid-item"><div class="grid-label">Midline Deviation:</div><div class="grid-value">${report.midline_deviation_mm?.toFixed(1) ?? '0.0'} mm</div></div>
      </div>

      <div class="section-title">Clinical Recommendations</div>
      <ol class="recommendation-list">
        ${report.recommendations && report.recommendations.length > 0 
          ? report.recommendations.map(r => `<li class="recommendation-item">${r}</li>`).join('')
          : '<li class="recommendation-item">No active detailing recommendations generated.</li>'
        }
      </ol>

      <div class="section-title">References</div>
      <div style="font-size: 11px; color: #64748b; line-height: 1.6; margin-bottom: 20px;">
        1. American Board of Orthodontics (ABO) Objective Grading System Guidelines<br />
        2. Andrews' Six Keys to Normal Occlusion Definitions<br />
        3. Raleigh Williams Finishing Protocols
      </div>

      <div class="score-box">
        <div class="score-label">Orthodontic Finishing Score</div>
        <div class="score-val">${Math.round(overallScore)}</div>
        <div class="score-status">${statusLabel}</div>
      </div>

      <div class="footer">
        OrthofinixAI Clinical Platform • HIPAA Compliant Secure Report
      </div>
    </body>
    </html>
  `;

  printWindow.document.write(printHtml);
  printWindow.document.close();
}
