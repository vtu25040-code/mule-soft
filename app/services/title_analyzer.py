import re
from typing import Dict, Any, List

class TitleAnalyzer:
    """
    Project Title Analysis Engine.
    Analyzes project titles and infers domain, subdomain, technical problem,
    objectives, keywords, algorithms, datasets, metrics, and initial research gaps.
    """
    
    DOMAIN_TAXONOMY = {
        "plant": {
            "domain": "Computer Vision & Agricultural Informatics",
            "subdomain": "Automated Plant Disease Diagnosis & Precision Agriculture",
            "problem": "Early and accurate identification of crop leaf pathology under varying environmental conditions.",
            "technologies": ["Convolutional Neural Networks (CNN)", "Deep Learning", "OpenCV", "PyTorch/TensorFlow", "Mobile Edge Deployment"],
            "datasets": ["PlantVillage Dataset", "Field Plant Pathology Dataset (FPPD)", "Custom Agricultural UAV Images"],
            "algorithms": ["ResNet-50", "EfficientNet-B4", "YOLOv8", "Vision Transformers (ViT)"],
            "metrics": ["Accuracy", "Precision", "Recall", "F1-Score", "Inference Latency (ms)", "FLOPs"],
            "challenges": ["Complex outdoor illumination", "Multi-disease overlap", "Low-power edge deployment", "Small dataset size"],
            "gaps": ["Lack of real-world field robustness", "High computational requirement of ViT models", "Class imbalance in rare diseases"]
        },
        "credit": {
            "domain": "Educational Informatics & Blockchain/AI Systems",
            "subdomain": "Academic Credit Automation & MOOC Quality Verification",
            "problem": "Manual verification, fragmentation, and potential fraud in academic credit transfers across online course platforms.",
            "technologies": ["Smart Contracts", "Hyperledger/Ethereum", "Natural Language Processing (NLP)", "Microservices Architecture"],
            "datasets": ["MOOC Learner Logs", "Coursera/edX Academic Course Metadata", "Higher Education Credit Alignment Corpus"],
            "algorithms": ["BERT-based Syllabus Matching", "Cosine Similarity Matrix", "Automated Validation Rules"],
            "metrics": ["Matching Precision", "Transfer Verification Speed", "System Throughput (TPS)", "User Satisfaction Index"],
            "challenges": ["Interoperability across university ERPs", "Varying credit rating systems", "Data privacy & GDPR compliance"],
            "gaps": ["Lack of automated semantic equivalence mapping", "Scalability limitations of public blockchains", "Inflexible rule engines"]
        },
        "medical": {
            "domain": "Biomedical Engineering & Healthcare AI",
            "subdomain": "Medical Image Analysis & Clinical Decision Support Systems",
            "problem": "High false-positive rate and subjective diagnostic variance in medical imaging.",
            "technologies": ["Deep Learning", "DICOM Processing", "Explainable AI (XAI)", "Federated Learning"],
            "datasets": ["MIMIC-CXR", "TCGA Biomarker Dataset", "ISIC Skin Cancer Archive"],
            "algorithms": ["U-Net Segmentation", "DenseNet-121", "Grad-CAM Explainability", "Attention U-Net"],
            "metrics": ["Dice Similarity Coefficient (DSC)", "AUC-ROC", "Sensitivity", "Specificity"],
            "challenges": ["Data privacy and HIPAA constraints", "Black-box nature of deep learning", "Domain shift across hospitals"],
            "gaps": ["Insufficient model interpretability for clinicians", "Generalizability across diverse scanners"]
        },
        "security": {
            "domain": "Cybersecurity & Network Intelligence",
            "subdomain": "AI-Driven Intrusion Detection & Threat Mitigation",
            "problem": "Detecting zero-day cyber threats in high-throughput network traffic with minimal false alarms.",
            "technologies": ["Graph Neural Networks (GNN)", "Anomalous Traffic Detection", "eBPF Packet Inspection"],
            "datasets": ["NSL-KDD", "CICIDS2017", "UNSW-NB15"],
            "algorithms": ["Autoencoders", "Random Forest", "Isolation Forests", "GCN Network Graph Analysis"],
            "metrics": ["Detection Rate (DR)", "False Positive Rate (FPR)", "Throughput (Gbps)", "Alert Resolution Time"],
            "challenges": ["Real-time line-rate processing", "Adversarial evasion attacks", "High traffic noise"],
            "gaps": ["Low robustness against adversarial packet perturbations", "High false alarm rate in encrypted traffic"]
        }
    }

    @staticmethod
    def analyze(title: str) -> Dict[str, Any]:
        title_clean = title.strip()
        title_lower = title_clean.lower()
        
        # Keyword extraction
        words = re.findall(r'\b[A-Za-z0-9\-]+\b', title_clean)
        stop_words = {'a', 'an', 'the', 'using', 'based', 'for', 'in', 'of', 'and', 'with', 'on', 'to', 'ai', 'driven', 'powered'}
        keywords = [w for w in words if w.lower() not in stop_words and len(w) > 2]
        
        # Match domain profile
        matched_profile = None
        for key, profile in TitleAnalyzer.DOMAIN_TAXONOMY.items():
            if key in title_lower:
                matched_profile = profile
                break
        
        if not matched_profile:
            # Generic smart synthesis fallback
            matched_profile = {
                "domain": "Artificial Intelligence & Computational Intelligence Systems",
                "subdomain": f"Applied AI & Automated Solutions for {keywords[0] if keywords else 'Engineering Problem'}",
                "problem": f"Efficiently modeling, automating, and optimizing performance in {title_clean}.",
                "technologies": ["Deep Learning", "Machine Learning Pipeline", "Cloud API", "Modern Web Framework"],
                "datasets": [f"Benchmark {keywords[0] if keywords else 'Domain'} Dataset", "Custom Empirical Data"],
                "algorithms": ["Transformer Architectures", "Gradient Boosting", "Ensemble Models", "Custom Heuristics"],
                "metrics": ["Accuracy", "Precision", "F1-Score", "Execution Time (s)", "Memory Footprint"],
                "challenges": ["Dataset scale and label noise", "Model computational complexity", "Real-world operational deployment"],
                "gaps": ["Limited evaluation on real-world noisy data", "Lack of end-to-end operational benchmark comparison"]
            }

        return {
            "project_title": title_clean,
            "research_domain": matched_profile["domain"],
            "subdomain": matched_profile["subdomain"],
            "main_technical_problem": matched_profile["problem"],
            "possible_objectives": [
                f"Design an end-to-end framework targeting {title_clean}.",
                "Develop an optimized computational pipeline to achieve state-of-the-art accuracy.",
                "Conduct comprehensive empirical evaluation against existing baseline approaches.",
                "Provide lightweight, real-world operational deployment capability."
            ],
            "important_keywords": keywords,
            "relevant_technologies": matched_profile["technologies"],
            "possible_datasets": matched_profile["datasets"],
            "possible_algorithms": matched_profile["algorithms"],
            "possible_metrics": matched_profile["metrics"],
            "potential_challenges": matched_profile["challenges"],
            "potential_research_gaps": matched_profile["gaps"]
        }
