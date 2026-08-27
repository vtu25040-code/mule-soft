import os
import shutil
from typing import List, Dict, Any
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.services.document_parser import DocumentParser
from app.services.title_analyzer import TitleAnalyzer
from app.services.paper_extractor import PaperExtractor
from app.services.knowledge_indexer import KnowledgeIndexer
from app.services.knowledge_graph import KnowledgeGraphEngine
from app.services.comparative_engine import ComparativeEngine
from app.services.gap_novelty_engine import GapNoveltyEngine
from app.services.ieee_writer import IEEEWriter
from app.services.quality_evaluator import QualityEvaluator
from app.services.plagiarism_checker import PlagiarismChecker
from app.services.exporter import ManuscriptExporter

app = FastAPI(
    title="AI-Powered IEEE Research Paper Preparation & Novelty Discovery Platform",
    description="Autonomous IEEE Literature Review, Research Gap Discovery, Novelty Analysis, Plagiarism Checker, and Paper Generation Platform.",
    version="2.1.0"
)

# Upload directory setup
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
EXPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "exports")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)

# In-memory Application Session State
STATE = {
    "project_title": "AI-Based Plant Disease Detection Using Deep Learning",
    "title_analysis": None,
    "project_docs": [],
    "ieee_papers": [],
    "rag_indexer": KnowledgeIndexer(),
    "knowledge_graph": None,
    "matrix": None,
    "differences": None,
    "similarity": None,
    "evolution": None,
    "gaps": [],
    "novelty": None,
    "contributions": [],
    "custom_outline": None,
    "generated_paper": None,
    "quality_audit": None,
    "plagiarism_audit": None,
    "current_step": 1
}

# Pre-populate title analysis on launch
STATE["title_analysis"] = TitleAnalyzer.analyze(STATE["project_title"])


@app.get("/api/status")
def get_status():
    return {
        "project_title": STATE["project_title"],
        "project_docs_count": len(STATE["project_docs"]),
        "ieee_papers_count": len(STATE["ieee_papers"]),
        "current_step": STATE["current_step"],
        "has_analysis": STATE["matrix"] is not None,
        "has_paper": STATE["generated_paper"] is not None,
        "plagiarism_index": STATE["plagiarism_audit"]["overall_plagiarism_index"] if STATE["plagiarism_audit"] else 2.5
    }


@app.post("/api/project/title")
def set_title(title: str = Form(...)):
    STATE["project_title"] = title.strip()
    STATE["title_analysis"] = TitleAnalyzer.analyze(STATE["project_title"])
    STATE["current_step"] = max(STATE["current_step"], 2)
    return {
        "status": "Success",
        "project_title": STATE["project_title"],
        "analysis": STATE["title_analysis"]
    }


@app.post("/api/upload/project-doc")
async def upload_project_doc(file: UploadFile = File(...)):
    if len(STATE["project_docs"]) >= 20:
        raise HTTPException(status_code=400, detail="Maximum limit of 20 project documents reached.")
        
    file_path = os.path.join(UPLOAD_DIR, f"proj_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    parsed = DocumentParser.parse_file(file_path, file.filename)
    doc_index = len(STATE["project_docs"]) + 1
    extracted = PaperExtractor.extract_project_doc(parsed, doc_index)
    extracted["raw_text"] = parsed["raw_text"]
    
    STATE["project_docs"].append(extracted)
    _reindex_and_analyze()
    return {"status": "Success", "uploaded_doc": extracted, "total_docs": len(STATE["project_docs"])}


@app.delete("/api/project-doc/{index}")
def delete_project_doc(index: int):
    if 0 <= index < len(STATE["project_docs"]):
        STATE["project_docs"].pop(index)
        _reindex_and_analyze()
        return {"status": "Success", "total_docs": len(STATE["project_docs"])}
    raise HTTPException(status_code=404, detail="Project document not found.")


@app.post("/api/upload/ieee-paper")
async def upload_ieee_paper(file: UploadFile = File(...)):
    if len(STATE["ieee_papers"]) >= 20:
        raise HTTPException(status_code=400, detail="Maximum limit of 20 IEEE reference papers reached.")
        
    file_path = os.path.join(UPLOAD_DIR, f"ieee_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    parsed = DocumentParser.parse_file(file_path, file.filename)
    paper_index = len(STATE["ieee_papers"]) + 1
    extracted = PaperExtractor.extract_ieee_paper(parsed, paper_index)
    extracted["raw_text"] = parsed["raw_text"]
    
    STATE["ieee_papers"].append(extracted)
    _reindex_and_analyze()
    return {"status": "Success", "uploaded_paper": extracted, "total_papers": len(STATE["ieee_papers"])}


@app.delete("/api/ieee-paper/{index}")
def delete_ieee_paper(index: int):
    if 0 <= index < len(STATE["ieee_papers"]):
        STATE["ieee_papers"].pop(index)
        _reindex_and_analyze()
        return {"status": "Success", "total_papers": len(STATE["ieee_papers"])}
    raise HTTPException(status_code=404, detail="IEEE paper not found.")


@app.get("/api/document-understanding")
def get_document_understanding():
    return {
        "project_documents": STATE["project_docs"],
        "ieee_papers": STATE["ieee_papers"]
    }


@app.get("/api/comparative-matrix")
def get_comparative_matrix():
    if not STATE["matrix"]:
        _reindex_and_analyze()
    return STATE["matrix"]


@app.get("/api/difference-analysis")
def get_difference_analysis():
    if not STATE["differences"]:
        _reindex_and_analyze()
    return STATE["differences"]


@app.get("/api/similarity-analysis")
def get_similarity_analysis():
    if not STATE["similarity"]:
        _reindex_and_analyze()
    return STATE["similarity"]


@app.get("/api/research-evolution")
def get_research_evolution():
    if not STATE["evolution"]:
        _reindex_and_analyze()
    return STATE["evolution"]


@app.get("/api/research-gaps")
def get_research_gaps():
    if not STATE["gaps"]:
        _reindex_and_analyze()
    return {"gaps": STATE["gaps"]}


@app.get("/api/novelty-analysis")
def get_novelty_analysis():
    if not STATE["novelty"]:
        _reindex_and_analyze()
    return STATE["novelty"]


@app.get("/api/contributions")
def get_contributions():
    if not STATE["contributions"]:
        _reindex_and_analyze()
    return {"contributions": STATE["contributions"]}


@app.get("/api/user-review-summary")
def get_user_review_summary():
    if not STATE["matrix"]:
        _reindex_and_analyze()
        
    return {
        "project_title": STATE["project_title"],
        "project_understanding": [d.get("project_understanding") for d in STATE["project_docs"]] if STATE["project_docs"] else "Default Title Configuration",
        "existing_research_summary": f"Analyzed {len(STATE['ieee_papers'])} reference papers.",
        "major_differences": STATE["differences"],
        "research_gaps": STATE["gaps"],
        "proposed_direction": f"Hybrid lightweight framework for {STATE['project_title']}.",
        "novel_contributions": STATE["contributions"],
        "missing_information": ["Actual execution logs for empirical test runs if available."],
        "outline": _get_default_outline() if not STATE["custom_outline"] else STATE["custom_outline"]
    }


@app.post("/api/generate-paper")
def generate_paper():
    _reindex_and_analyze()
    
    manuscript = IEEEWriter.generate_manuscript(
        project_title=STATE["project_title"],
        title_analysis=STATE["title_analysis"],
        project_docs=STATE["project_docs"],
        papers=STATE["ieee_papers"],
        gaps=STATE["gaps"],
        contributions=STATE["contributions"],
        rag_indexer=STATE["rag_indexer"],
        custom_outline=STATE["custom_outline"]
    )
    
    STATE["generated_paper"] = manuscript
    STATE["quality_audit"] = QualityEvaluator.audit(manuscript, STATE["project_docs"], STATE["ieee_papers"])
    STATE["plagiarism_audit"] = PlagiarismChecker.audit_manuscript(manuscript["full_text"], STATE["ieee_papers"], STATE["project_docs"])
    STATE["current_step"] = 17
    
    return {
        "status": "Success",
        "manuscript": manuscript,
        "quality_audit": STATE["quality_audit"],
        "plagiarism_audit": STATE["plagiarism_audit"]
    }


@app.get("/api/quality-checker")
def get_quality_checker():
    if not STATE["generated_paper"]:
        generate_paper()
    return STATE["quality_audit"]


@app.get("/api/plagiarism-check")
def get_plagiarism_check():
    if not STATE["generated_paper"]:
        generate_paper()
    if not STATE["plagiarism_audit"]:
        STATE["plagiarism_audit"] = PlagiarismChecker.audit_manuscript(STATE["generated_paper"]["full_text"], STATE["ieee_papers"], STATE["project_docs"])
    return STATE["plagiarism_audit"]


@app.get("/api/export/{format_type}")
def export_manuscript(format_type: str):
    if not STATE["generated_paper"]:
        generate_paper()
        
    m = STATE["generated_paper"]
    safe_title = "".join([c if c.isalnum() else "_" for c in STATE["project_title"]])[:30]
    
    if format_type == "markdown":
        file_path = os.path.join(EXPORTS_DIR, f"{safe_title}_IEEE_Paper.md")
        ManuscriptExporter.export_markdown(m["full_text"], file_path)
        return FileResponse(file_path, filename=f"{safe_title}_IEEE_Paper.md", media_type="text/markdown")
    elif format_type == "latex":
        file_path = os.path.join(EXPORTS_DIR, f"{safe_title}_IEEE_Paper.tex")
        ManuscriptExporter.export_latex(m, file_path)
        return FileResponse(file_path, filename=f"{safe_title}_IEEE_Paper.tex", media_type="application/x-tex")
    elif format_type == "docx":
        file_path = os.path.join(EXPORTS_DIR, f"{safe_title}_IEEE_Paper.docx")
        ManuscriptExporter.export_docx(m, file_path)
        return FileResponse(file_path, filename=f"{safe_title}_IEEE_Paper.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    else:
        raise HTTPException(status_code=400, detail="Invalid export format requested.")


def _reindex_and_analyze():
    docs_for_indexing = []
    for d in STATE["project_docs"]:
        docs_for_indexing.append({"filename": d["filename"], "type": "Project Document", "raw_text": d.get("raw_text", "")})
    for p in STATE["ieee_papers"]:
        docs_for_indexing.append({"filename": p["filename"], "type": "IEEE Reference Paper", "raw_text": p.get("raw_text", "")})
        
    STATE["rag_indexer"].index_documents(docs_for_indexing)
    STATE["knowledge_graph"] = KnowledgeGraphEngine.build_graph(STATE["ieee_papers"], STATE["project_docs"])
    
    STATE["matrix"] = ComparativeEngine.build_matrix(STATE["ieee_papers"])
    STATE["differences"] = ComparativeEngine.analyze_differences(STATE["ieee_papers"])
    STATE["similarity"] = ComparativeEngine.analyze_similarity(STATE["ieee_papers"])
    STATE["evolution"] = ComparativeEngine.analyze_evolution(STATE["ieee_papers"])
    
    STATE["gaps"] = GapNoveltyEngine.discover_gaps(STATE["ieee_papers"], STATE["project_title"])
    STATE["novelty"] = GapNoveltyEngine.analyze_novelty(STATE["ieee_papers"], STATE["project_docs"], STATE["project_title"])
    STATE["contributions"] = GapNoveltyEngine.generate_contributions(STATE["project_title"], STATE["gaps"])
    
    if STATE["generated_paper"]:
        STATE["plagiarism_audit"] = PlagiarismChecker.audit_manuscript(STATE["generated_paper"]["full_text"], STATE["ieee_papers"], STATE["project_docs"])


def _get_default_outline():
    return [
        {"number": "I", "title": "INTRODUCTION"},
        {"number": "II", "title": "RELATED WORK"},
        {"number": "III", "title": "PROBLEM STATEMENT"},
        {"number": "IV", "title": "PROPOSED METHODOLOGY"},
        {"number": "V", "title": "SYSTEM ARCHITECTURE"},
        {"number": "VI", "title": "IMPLEMENTATION DETAILS"},
        {"number": "VII", "title": "EXPERIMENTAL SETUP"},
        {"number": "VIII", "title": "RESULTS AND DISCUSSION"},
        {"number": "IX", "title": "COMPARATIVE ANALYSIS"},
        {"number": "X", "title": "LIMITATIONS"},
        {"number": "XI", "title": "FUTURE WORK"},
        {"number": "XII", "title": "CONCLUSION"}
    ]

# Serve Static UI
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
