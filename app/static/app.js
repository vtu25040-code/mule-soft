// AI-Powered IEEE Research Platform - Frontend Controller

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initUploaders();
    fetchStatus();
    loadTitleAnalysis();
});

// Module Navigation
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetModule = item.getAttribute('data-module');
            
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');
            
            document.querySelectorAll('.module-section').forEach(sec => sec.classList.remove('active'));
            const activeSec = document.getElementById(`module-${targetModule}`);
            if (activeSec) {
                activeSec.classList.add('active');
            }
            
            // Trigger specific module loads
            onModuleSwitch(targetModule);
        });
    });
}

function onModuleSwitch(moduleKey) {
    if (moduleKey === 'matrix') loadComparativeMatrix();
    else if (moduleKey === 'difference') loadDifferenceAnalysis();
    else if (moduleKey === 'similarity') loadSimilarityAnalysis();
    else if (moduleKey === 'evolution') loadResearchEvolution();
    else if (moduleKey === 'gaps') loadResearchGaps();
    else if (moduleKey === 'novelty') loadNoveltyAnalysis();
    else if (moduleKey === 'contributions') loadContributions();
    else if (moduleKey === 'review') loadUserReview();
    else if (moduleKey === 'understanding') loadDocumentUnderstanding();
    else if (moduleKey === 'quality') loadQualityChecker();
}

// Fetch Application Status
async function fetchStatus() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        
        document.getElementById('stat-docs-count').innerText = data.project_docs_count;
        document.getElementById('stat-papers-count').innerText = data.ieee_papers_count;
        document.getElementById('active-step-num').innerText = data.current_step;
        
        if (data.project_title) {
            document.getElementById('project-title-input').value = data.project_title;
        }
    } catch (e) {
        console.error('Status fetch error:', e);
    }
}

// Module 1: Project Title Submit & Analysis
async function analyzeTitle() {
    const titleInput = document.getElementById('project-title-input').value;
    if (!titleInput.trim()) return alert('Please enter a project title.');
    
    const formData = new FormData();
    formData.append('title', titleInput);
    
    try {
        const res = await fetch('/api/project/title', { method: 'POST', body: formData });
        const data = await res.json();
        renderTitleAnalysis(data.analysis);
        fetchStatus();
    } catch (e) {
        alert('Error analyzing title: ' + e);
    }
}

async function loadTitleAnalysis() {
    try {
        const res = await fetch('/api/status');
        const status = await res.json();
        if (status.project_title) {
            const formData = new FormData();
            formData.append('title', status.project_title);
            const res2 = await fetch('/api/project/title', { method: 'POST', body: formData });
            const data = await res2.json();
            renderTitleAnalysis(data.analysis);
        }
    } catch (e) {
        console.error(e);
    }
}

function renderTitleAnalysis(analysis) {
    const container = document.getElementById('title-analysis-container');
    if (!analysis || !container) return;
    
    container.innerHTML = `
        <div class="card">
            <div class="card-title">🔍 Project Title Analysis</div>
            <div class="grid-2">
                <div>
                    <p><strong>Research Domain:</strong> ${analysis.research_domain}</p>
                    <p><strong>Subdomain:</strong> ${analysis.subdomain}</p>
                    <p><strong>Main Technical Problem:</strong> ${analysis.main_technical_problem}</p>
                    <p><strong>Keywords:</strong> ${analysis.important_keywords.join(', ')}</p>
                </div>
                <div>
                    <p><strong>Technologies:</strong> ${analysis.relevant_technologies.join(', ')}</p>
                    <p><strong>Possible Datasets:</strong> ${analysis.possible_datasets.join(', ')}</p>
                    <p><strong>Algorithms:</strong> ${analysis.possible_algorithms.join(', ')}</p>
                    <p><strong>Metrics:</strong> ${analysis.possible_metrics.join(', ')}</p>
                </div>
            </div>
            <div style="margin-top:16px;">
                <p><strong>Potential Research Gaps:</strong></p>
                <ul>
                    ${analysis.potential_research_gaps.map(g => `<li>${g}</li>`).join('')}
                </ul>
            </div>
        </div>
    `;
}

// Module 2 & 3: File Uploads
function initUploaders() {
    setupDropzone('proj-dropzone', 'proj-file-input', '/api/upload/project-doc', loadProjectDocs);
    setupDropzone('ieee-dropzone', 'ieee-file-input', '/api/upload/ieee-paper', loadIEEEPapers);
}

function setupDropzone(dropzoneId, inputId, endpoint, callback) {
    const dropzone = document.getElementById(dropzoneId);
    const input = document.getElementById(inputId);
    if (!dropzone || !input) return;
    
    dropzone.addEventListener('click', () => input.click());
    
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.style.backgroundColor = 'rgba(2, 132, 199, 0.2)';
    });
    
    dropzone.addEventListener('dragleave', () => {
        dropzone.style.backgroundColor = 'rgba(2, 132, 199, 0.05)';
    });
    
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.style.backgroundColor = 'rgba(2, 132, 199, 0.05)';
        if (e.dataTransfer.files.length) {
            handleFileUpload(e.dataTransfer.files[0], endpoint, callback);
        }
    });
    
    input.addEventListener('change', () => {
        if (input.files.length) {
            handleFileUpload(input.files[0], endpoint, callback);
        }
    });
}

async function handleFileUpload(file, endpoint, callback) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const res = await fetch(endpoint, { method: 'POST', body: formData });
        const data = await res.json();
        if (res.ok) {
            alert('File uploaded successfully: ' + file.name);
            fetchStatus();
            if (callback) callback();
        } else {
            alert('Upload failed: ' + (data.detail || 'Unknown error'));
        }
    } catch (e) {
        alert('Upload error: ' + e);
    }
}

async function loadProjectDocs() {
    const res = await fetch('/api/document-understanding');
    const data = await res.json();
    const list = document.getElementById('proj-docs-list');
    if (!list) return;
    
    list.innerHTML = data.project_documents.map((d, i) => `
        <tr>
            <td>${d.filename}</td>
            <td>${d.doc_type}</td>
            <td>${(d.size_bytes / 1024).toFixed(1)} KB</td>
            <td><span class="badge badge-explicit">Uploaded</span></td>
            <td><span class="badge badge-explicit">Analyzed</span></td>
            <td><button class="btn btn-secondary" onclick="deleteDoc('project-doc', ${i})">Remove</button></td>
        </tr>
    `).join('') || '<tr><td colspan="6">No project documents uploaded yet.</td></tr>';
}

async function loadIEEEPapers() {
    const res = await fetch('/api/document-understanding');
    const data = await res.json();
    const list = document.getElementById('ieee-papers-list');
    if (!list) return;
    
    list.innerHTML = data.ieee_papers.map((p, i) => `
        <tr>
            <td>Paper ${i+1}</td>
            <td>${p.bibliographic.title.val}</td>
            <td>${p.bibliographic.authors.val}</td>
            <td>${p.bibliographic.year.val}</td>
            <td>${p.bibliographic.venue.val}</td>
            <td>${p.bibliographic.doi.val}</td>
            <td><button class="btn btn-secondary" onclick="deleteDoc('ieee-paper', ${i})">Delete</button></td>
        </tr>
    `).join('') || '<tr><td colspan="7">No IEEE papers uploaded yet.</td></tr>';
}

async function deleteDoc(type, index) {
    if (!confirm('Are you sure you want to remove this document?')) return;
    await fetch(`/api/${type}/${index}`, { method: 'DELETE' });
    fetchStatus();
    if (type === 'project-doc') loadProjectDocs();
    else loadIEEEPapers();
}

// Module 4 & 5: Document Understanding
async function loadDocumentUnderstanding() {
    const res = await fetch('/api/document-understanding');
    const data = await res.json();
    const container = document.getElementById('document-understanding-container');
    if (!container) return;
    
    container.innerHTML = `
        <div class="card">
            <div class="card-title">📄 Extracted Information (Explicit vs Inferred)</div>
            <h3>Project Documents (${data.project_documents.length})</h3>
            ${data.project_documents.map(d => `
                <div style="margin-bottom:12px; padding:12px; background:rgba(0,0,0,0.2); border-radius:6px;">
                    <strong>${d.filename}</strong>
                    <p>Problem: ${d.project_understanding.problem.val} <span class="badge badge-${d.project_understanding.problem.mode === 'Explicitly Stated' ? 'explicit' : 'inferred'}">${d.project_understanding.problem.mode}</span></p>
                    <p>Methodology: ${d.project_understanding.methodology.val} <span class="badge badge-${d.project_understanding.methodology.mode === 'Explicitly Stated' ? 'explicit' : 'inferred'}">${d.project_understanding.methodology.mode}</span></p>
                </div>
            `).join('')}
            <h3 style="margin-top:20px;">IEEE Reference Papers (${data.ieee_papers.length})</h3>
            ${data.ieee_papers.map(p => `
                <div style="margin-bottom:12px; padding:12px; background:rgba(0,0,0,0.2); border-radius:6px;">
                    <strong>Paper ${p.paper_no}: ${p.bibliographic.title.val}</strong>
                    <p>Algorithm: ${p.research.algorithm.val} <span class="badge badge-${p.research.algorithm.mode === 'Explicitly Stated' ? 'explicit' : 'inferred'}">${p.research.algorithm.mode}</span></p>
                    <p>Dataset: ${p.research.dataset.val} <span class="badge badge-${p.research.dataset.mode === 'Explicitly Stated' ? 'explicit' : 'inferred'}">${p.research.dataset.mode}</span></p>
                </div>
            `).join('')}
        </div>
    `;
}

// Module 6: Comparative Matrix
async function loadComparativeMatrix() {
    const res = await fetch('/api/comparative-matrix');
    const data = await res.json();
    const container = document.getElementById('matrix-container');
    if (!container || !data.columns) return;
    
    let html = `
        <div class="matrix-container">
            <table class="matrix-table">
                <thead>
                    <tr>
                        <th class="param-col">Parameter</th>
                        ${data.columns.map(c => `<th>${c.paper_key}<br><small style="font-weight:normal;color:#94A3B8;">${c.title.substring(0,25)}...</small></th>`).join('')}
                    </tr>
                </thead>
                <tbody>
                    ${data.matrix.map(row => `
                        <tr>
                            <td class="param-col">${row.parameter}</td>
                            ${data.columns.map(c => `<td>${row.values[c.paper_key] || 'N/A'}</td>`).join('')}
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
    container.innerHTML = html;
}

// Module 8: Difference Analysis
async function loadDifferenceAnalysis() {
    const res = await fetch('/api/difference-analysis');
    const data = await res.json();
    const container = document.getElementById('difference-container');
    if (!container) return;
    
    container.innerHTML = data.pairwise_comparisons.map(pair => `
        <div class="card">
            <div class="card-title">⚖️ ${pair.pair}: ${pair.title_1.substring(0,30)}... vs ${pair.title_2.substring(0,30)}...</div>
            ${pair.differences.map(d => `
                <div style="margin-bottom:12px; background:rgba(0,0,0,0.2); padding:10px; border-radius:6px;">
                    <strong>Aspect: ${d.aspect}</strong>
                    <p style="color:#94A3B8;">• ${pair.title_1.substring(0,20)}: ${d.paper_1}</p>
                    <p style="color:#94A3B8;">• ${pair.title_2.substring(0,20)}: ${d.paper_2}</p>
                    <p style="color:#38BDF8; margin-top:4px;"><strong>Technical Significance:</strong> ${d.technical_significance}</p>
                </div>
            `).join('')}
        </div>
    `).join('') || '<p>Upload reference papers to generate pairwise difference analysis.</p>';
}

// Module 9: Similarity Analysis
async function loadSimilarityAnalysis() {
    const res = await fetch('/api/similarity-analysis');
    const data = await res.json();
    const container = document.getElementById('similarity-container');
    if (!container) return;
    
    container.innerHTML = Object.keys(data.clusters).map(clusterName => `
        <div class="card">
            <div class="card-title">🏷️ ${clusterName} (${data.clusters[clusterName].length} Papers)</div>
            ${data.clusters[clusterName].map(item => `
                <p>• <strong>Paper ${item.paper_no}:</strong> ${item.title} <em>(Model: ${item.algorithm})</em></p>
            `).join('')}
        </div>
    `).join('') || '<p>No papers uploaded yet.</p>';
}

// Module 10: Research Evolution
async function loadResearchEvolution() {
    const res = await fetch('/api/research-evolution');
    const data = await res.json();
    const container = document.getElementById('evolution-container');
    if (!container) return;
    
    container.innerHTML = `
        <div class="card">
            <div class="card-title">⏳ Chronological Research Evolution Timeline</div>
            ${data.timeline.map(item => `
                <div style="border-left: 3px solid #0284C7; padding-left: 16px; margin-bottom: 16px;">
                    <span class="badge badge-explicit">${item.year}</span>
                    <strong style="margin-left:8px; color:white;">Method: ${item.method}</strong>
                    <p style="font-size:0.85rem; color:#94A3B8;">Stack: ${item.technology} | Result: ${item.result}</p>
                    <p style="font-size:0.85rem; color:#F87171;">Limitation: ${item.limitation}</p>
                    <p style="font-size:0.85rem; color:#38BDF8;">Direction: ${item.research_direction}</p>
                </div>
            `).join('')}
        </div>
    `;
}

// Module 10 & 11: Research Gap Discovery
async function loadResearchGaps() {
    const res = await fetch('/api/research-gaps');
    const data = await res.json();
    const container = document.getElementById('gaps-container');
    if (!container) return;
    
    container.innerHTML = data.gaps.map(gap => `
        <div class="gap-card">
            <div class="gap-title">🎯 [${gap.category}] ${gap.title}</div>
            <div class="gap-meta">Supporting Literature: ${gap.supporting_papers}</div>
            <p><strong>Evidence:</strong> ${gap.evidence}</p>
            <p style="color:#FBBF24; margin-top:4px;"><strong>Why It Matters:</strong> ${gap.why_it_matters}</p>
            <p style="color:#34D399; margin-top:4px;"><strong>How User Project Addresses It:</strong> ${gap.how_project_addresses_it}</p>
        </div>
    `).join('');
}

// Module 12: Novelty Analysis
async function loadNoveltyAnalysis() {
    const res = await fetch('/api/novelty-analysis');
    const data = await res.json();
    const container = document.getElementById('novelty-container');
    if (!container) return;
    
    container.innerHTML = `
        <div class="card">
            <div class="card-title">✨ Defensible Novelty & Differentiation Matrix</div>
            <p style="margin-bottom:12px;"><strong>Novelty Confidence Claim:</strong> <span class="badge badge-explicit">${data.novelty_confidence}</span></p>
            <p style="color:#94A3B8; margin-bottom:16px;">${data.confidence_explanation}</p>
            <table class="table">
                <tr><th>Dimension</th><th>Existing Literature</th><th>User's Project</th></tr>
                <tr><td>Technical Architecture</td><td>${data.comparison_matrix.existing_research}</td><td>${data.comparison_matrix.user_project}</td></tr>
                <tr><td>Methodology</td><td>High-parameter static models</td><td>${data.comparison_matrix.methodological_difference}</td></tr>
                <tr><td>Practical Impact</td><td>Offline lab validation</td><td>${data.comparison_matrix.practical_difference}</td></tr>
            </table>
        </div>
    `;
}

// Module 13: Contribution Generator
async function loadContributions() {
    const res = await fetch('/api/contributions');
    const data = await res.json();
    const container = document.getElementById('contributions-container');
    if (!container) return;
    
    container.innerHTML = `
        <div class="card">
            <div class="card-title">💡 Generated Realistic Research Contributions</div>
            ${data.contributions.map(c => `<p style="margin-bottom:10px; padding:10px; background:rgba(0,0,0,0.2); border-radius:6px; font-weight:500;">${c}</p>`).join('')}
        </div>
    `;
}

// Module 23: Pre-Generation User Review
async function loadUserReview() {
    const res = await fetch('/api/user-review-summary');
    const data = await res.json();
    const container = document.getElementById('user-review-container');
    if (!container) return;
    
    container.innerHTML = `
        <div class="card">
            <div class="card-title">📋 Pre-Generation Research Synthesis Review</div>
            <p><strong>Project Title:</strong> ${data.project_title}</p>
            <p><strong>Existing Research Summary:</strong> ${data.existing_research_summary}</p>
            <p><strong>Proposed Research Direction:</strong> ${data.proposed_direction}</p>
            <h4 style="margin-top:16px; margin-bottom:8px;">Editable IEEE Paper Outline</h4>
            <ul style="margin-left:20px;">
                ${data.outline.map(s => `<li>Section ${s.number}: ${s.title}</li>`).join('')}
            </ul>
            <div style="margin-top:20px;">
                <button class="btn btn-success" onclick="triggerPaperGeneration()">Generate Complete IEEE Manuscript</button>
            </div>
        </div>
    `;
}

// Module 14: IEEE Manuscript Generator
async function triggerPaperGeneration() {
    alert('Generating IEEE Paper Manuscript with Citation Intelligence...');
    try {
        const res = await fetch('/api/generate-paper', { method: 'POST' });
        const data = await res.json();
        renderManuscript(data.manuscript);
        
        // Switch view to paper generator module
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        document.querySelector('[data-module="generator"]').classList.add('active');
        document.querySelectorAll('.module-section').forEach(sec => sec.classList.remove('active'));
        document.getElementById('module-generator').classList.add('active');
        
        fetchStatus();
    } catch (e) {
        alert('Generation error: ' + e);
    }
}

function renderManuscript(manuscript) {
    const container = document.getElementById('manuscript-viewer');
    if (!container || !manuscript) return;
    
    container.innerHTML = `
        <div class="manuscript-box">
            <h1>${manuscript.title}</h1>
            <p style="text-align:center; font-style:italic;">Author Name 1, Author Name 2<br>Department of Computer Science & Engineering</p>
            <hr style="margin:16px 0; border-color:#334155;">
            <p><strong>Abstract</strong>—${manuscript.abstract}</p>
            <p><strong>Index Terms</strong>—${manuscript.keywords}</p>
            
            ${manuscript.sections.map(s => `
                <h2>${s.number}. ${s.title}</h2>
                <div style="white-space: pre-wrap;">${s.content}</div>
            `).join('')}
            
            <h2>REFERENCES</h2>
            ${manuscript.references.map(r => `
                <p>[${r.id}] ${r.formatted_citation}</p>
            `).join('')}
        </div>
    `;
}

// Module 16 & 20: Quality Audit Checker & Score Card
async function loadQualityChecker() {
    const res = await fetch('/api/quality-checker');
    const data = await res.json();
    const container = document.getElementById('quality-container');
    if (!container || !data.scores) return;
    
    const scores = data.scores;
    container.innerHTML = `
        <div class="card">
            <div class="card-title">📊 IEEE Research Readiness Quality Audit Report</div>
            <div class="stat-box" style="margin-bottom:20px; text-align:center;">
                <div class="stat-label">Overall Research Readiness Score</div>
                <div class="stat-val" style="font-size:2.5rem;">${scores.overall_research_readiness.score} / 10</div>
                <p style="color:#94A3B8; font-size:0.85rem;">${scores.overall_research_readiness.explanation}</p>
            </div>
            
            ${Object.keys(scores).filter(k => k !== 'overall_research_readiness').map(key => `
                <div class="score-meter-container">
                    <span style="width:200px; font-weight:600; text-transform:capitalize;">${key.replace('_', ' ')}</span>
                    <div class="score-bar-bg">
                        <div class="score-bar-fill" style="width:${scores[key].score * 10}%;"></div>
                    </div>
                    <span class="score-val">${scores[key].score}/10</span>
                </div>
                <p style="font-size:0.8rem; color:#94A3B8; margin-bottom:12px; margin-left:200px;">${scores[key].explanation}</p>
            `).join('')}
        </div>
    `;
}

// Module 17: Exporter
function downloadExport(formatType) {
    window.location.href = `/api/export/${formatType}`;
}
