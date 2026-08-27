from typing import List, Dict, Any

class KnowledgeGraphEngine:
    """
    Multi-Document Knowledge Graph Builder.
    Constructs entity-relationship graphs linking:
    Paper -> Problem -> Method -> Dataset -> Result -> Limitation -> Gap
    and User Project -> Method -> Dataset -> Contribution -> Gap
    """

    @staticmethod
    def _safe_get_val(obj: Any, default: str = "") -> str:
        if isinstance(obj, dict):
            return str(obj.get("val", default))
        if isinstance(obj, str):
            return obj
        return default

    @staticmethod
    def build_graph(papers: List[Dict[str, Any]], project_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        nodes = []
        edges = []
        
        # User Project Node
        nodes.append({"id": "user_project", "label": "User's Project", "type": "Project", "color": "#3B82F6"})
        
        for idx, doc in enumerate(project_docs, 1):
            p_under = doc.get("project_understanding", {}) if isinstance(doc, dict) else {}
            meth_val = KnowledgeGraphEngine._safe_get_val(p_under.get("methodology"), "Custom Method")
            
            nodes.append({"id": f"proj_method_{idx}", "label": f"Method: {meth_val[:30]}", "type": "Method", "color": "#10B981"})
            edges.append({"source": "user_project", "target": f"proj_method_{idx}", "relation": "USES_METHOD"})
            
            nodes.append({"id": f"proj_gap_{idx}", "label": "Gap Addressed", "type": "Gap", "color": "#EF4444"})
            edges.append({"source": "user_project", "target": f"proj_gap_{idx}", "relation": "SOLVES_GAP"})

        # Paper Nodes
        for p in papers:
            p_no = p.get("paper_no", 1) if isinstance(p, dict) else 1
            p_id = f"paper_{p_no}"
            bib = p.get("bibliographic", {}) if isinstance(p, dict) else {}
            res = p.get("research", {}) if isinstance(p, dict) else {}
            
            title_val = KnowledgeGraphEngine._safe_get_val(bib.get("title") if isinstance(bib, dict) else bib, f"Paper {p_no}")
            nodes.append({"id": p_id, "label": f"P{p_no}: {title_val[:35]}...", "type": "Paper", "color": "#6366F1"})
            
            prob_id = f"prob_{p_no}"
            nodes.append({"id": prob_id, "label": f"Problem P{p_no}", "type": "Problem", "color": "#F59E0B"})
            edges.append({"source": p_id, "target": prob_id, "relation": "ADDRESSES"})
            
            meth_id = f"meth_{p_no}"
            alg_val = KnowledgeGraphEngine._safe_get_val(res.get("algorithm") if isinstance(res, dict) else res, "ML Model")
            nodes.append({"id": meth_id, "label": f"Method: {alg_val[:25]}", "type": "Method", "color": "#10B981"})
            edges.append({"source": p_id, "target": meth_id, "relation": "PROPOSES"})
            
            lim_id = f"lim_{p_no}"
            nodes.append({"id": lim_id, "label": f"Limitation P{p_no}", "type": "Limitation", "color": "#EC4899"})
            edges.append({"source": meth_id, "target": lim_id, "relation": "HAS_LIMITATION"})

        return {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "nodes": nodes,
            "edges": edges
        }
