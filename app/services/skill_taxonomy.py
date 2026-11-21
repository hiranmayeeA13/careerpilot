"""
Deterministic keyword-based skill extraction.

This is intentionally NOT an LLM call: per the project's own architecture
rule ("LLMs are never used to compute or verify numbers, scores, weights,
or states"), skill extraction from resumes and job descriptions has to be
reproducible and auditable, so it runs on a keyword/synonym match against a
known skill taxonomy, with simple frequency-based weighting.
"""
import re
from collections import Counter
from typing import Dict, List

# skill_name -> list of surface forms / synonyms to match in free text (case-insensitive)
SKILL_SYNONYMS: Dict[str, List[str]] = {
    "Linux": ["linux", "bash", "shell scripting", "unix"],
    "Networking": ["networking", "tcp/ip", "dns", "load balanc", "vpc", "subnet"],
    "Docker": ["docker", "containeriz", "dockerfile", "docker-compose"],
    "Kubernetes": ["kubernetes", "k8s", "helm", "kubectl"],
    "CI/CD": ["ci/cd", "continuous integration", "continuous deployment", "jenkins", "github actions", "gitlab ci"],
    "Cloud/AWS": ["aws", "amazon web services", "ec2", "s3", "lambda", "cloudformation"],
    "Cloud Architecture": ["cloud architecture", "multi-cloud", "well-architected"],
    "Security & IAM": ["iam", "security group", "oauth", "zero trust", "encryption"],
    "DevOps & IaC": ["terraform", "infrastructure as code", "iac", "ansible", "pulumi"],
    "Cost Optimization": ["cost optimization", "finops", "reserved instances"],
    "Data Structures & Algorithms": ["data structures", "algorithms", "leetcode", "dsa", "big-o"],
    "Python": ["python", "django", "flask", "fastapi", "pandas", "numpy"],
    "SQL & Databases": ["sql", "postgres", "mysql", "database", "nosql", "mongodb", "indexing"],
    "API Design & REST": ["rest api", "restful", "api design", "graphql", "openapi", "swagger"],
    "System Design": ["system design", "distributed systems", "scalab", "microservices", "load balancing"],
    "JavaScript": ["javascript", "typescript", "node.js", "nodejs"],
    "React": ["react", "react.js", "redux", "next.js"],
    "Machine Learning": ["machine learning", "scikit-learn", "tensorflow", "pytorch", "ml model"],
    "Communication": ["presented", "communicat", "stakeholder", "documentation"],
    "Testing & QA": ["unit test", "pytest", "test coverage", "qa", "test automation"],
    "Git & Version Control": ["git", "github", "gitlab", "version control", "pull request"],
}

ALL_SKILLS = list(SKILL_SYNONYMS.keys())


def extract_skill_counts(text: str) -> Dict[str, int]:
    """Return {skill: occurrence_count} for every skill with >=1 keyword hit in text."""
    if not text:
        return {}
    lowered = text.lower()
    counts: Counter = Counter()
    for skill, synonyms in SKILL_SYNONYMS.items():
        hits = 0
        for syn in synonyms:
            hits += len(re.findall(re.escape(syn.lower()), lowered))
        if hits > 0:
            counts[skill] = hits
    return dict(counts)


def mastery_from_resume_count(count: int) -> int:
    """Heuristic: more distinct mentions in a resume => assumed higher self-reported mastery."""
    return max(20, min(70, 25 + count * 10))
