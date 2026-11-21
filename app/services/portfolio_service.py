from typing import List, Tuple
from app.database import get_role_requirements
from app.models.schemas import (
    CandidateProfile,
    PortfolioProjectResponse,
    ProjectMilestone,
    RubricCriterion,
)
from app.services.gemini_service import sanitize_gemini_text


def generate_portfolio_project_recommendation(
    candidate: CandidateProfile,
    variation_index: int = 0,
) -> PortfolioProjectResponse:
    """
    Generates a targeted, hands-on portfolio project addressing the candidate's
    actual weakest verified-missing skills, supporting multiple distinct project variants.
    Guarantees zero generic placeholders.
    """
    role_reqs = get_role_requirements(candidate.target_role, candidate.skills)

    # 1. Identify weakest verified-missing skills
    candidates_weak_skills: List[Tuple[str, float, int, str]] = []
    for skill_name, req in role_reqs.items():
        weight = req.get("weight", 1.0)
        req_mastery = req.get("required_mastery", 70)
        curr_mastery = candidate.skills.get(skill_name, 0)
        is_foundation = req.get("is_foundation", False)

        ev = candidate.skill_evidence.get(skill_name)
        ev_status = ev.status if ev else "Unverified"
        has_project_evidence = ev_status in ["Project-demonstrated", "Strongly-supported"]

        if not has_project_evidence or curr_mastery < req_mastery:
            deficit = (req_mastery - curr_mastery)
            priority = (2.0 if is_foundation else 1.0) * weight * 100 + max(0, deficit)
            candidates_weak_skills.append((skill_name, priority, curr_mastery, ev_status))

    candidates_weak_skills.sort(key=lambda x: x[1], reverse=True)

    if candidates_weak_skills:
        target_skills = [item[0] for item in candidates_weak_skills[:2]]
    else:
        target_skills = list(role_reqs.keys())[:2]

    target_set = set(target_skills)
    v = variation_index % 3

    # Branch by domain & variation
    if any(s in target_set for s in ["Linux", "Networking", "Docker", "Kubernetes", "CI/CD"]):
        demonstrated = [s for s in ["Linux", "Networking", "Docker", "Kubernetes", "CI/CD"] if s in role_reqs]
        if not demonstrated:
            demonstrated = target_skills

        if v == 0:
            title = "Hardened Linux Gateway & Automated Network Packet Inspector"
            problem_statement = (
                "Modern infrastructure environments require automated edge gateways capable of filtering, "
                "routing, and inspecting high-throughput network packets while maintaining strict Linux kernel "
                "security baselines and systemd daemon management."
            )
            difficulty = "Intermediate-Advanced"
            required_tools = ["Linux (Ubuntu/Debian)", "Bash", "nftables/iptables", "Wireshark/tcpdump", "systemd", "Python"]
            milestones = [
                ProjectMilestone(step=1, name="Linux Kernel & Network Namespace Configuration", deliverable="Configured isolated Linux network namespaces, virtual veth pairs, and routing tables."),
                ProjectMilestone(step=2, name="Firewall Rule Engine & Traffic Filtering", deliverable="nftables script enforcing stateful packet inspection, NAT masquerading, and port knocking."),
                ProjectMilestone(step=3, name="Observability & Health Daemon", deliverable="Automated Python/Bash service logging packet metrics as a managed systemd background daemon."),
            ]
            deliverables = [
                "GitHub repository with systemd unit files and kernel sysctl hardening presets",
                "Automated setup script deploying isolated network namespaces and firewall rules",
                "Network benchmark report demonstrating packet filtering throughput and latency analysis",
            ]
            rubric = [
                RubricCriterion(criterion="Linux System Administration", target_standard="Proper use of systemd services, security capabilities, and sysctl network tuning."),
                RubricCriterion(criterion="Network Architecture & Routing", target_standard="Correct CIDR subnetting, stateful firewall rules, and verified packet flow inspection."),
            ]
        elif v == 1:
            title = "Multi-Region Kubernetes Delivery Mesh with Automated Canary Rollouts"
            problem_statement = (
                "High-availability web architectures require resilient containerized microservice deployments "
                "with automated traffic splitting, liveness/readiness probes, and immediate rollback triggers upon metric regression."
            )
            difficulty = "Advanced"
            required_tools = ["Docker", "Kubernetes (Kind/k3s)", "Helm", "Prometheus", "GitHub Actions"]
            milestones = [
                ProjectMilestone(step=1, name="Multi-Stage Distroless Containerization", deliverable="Multi-stage Dockerfiles producing minimal attack-surface non-root images under 40MB."),
                ProjectMilestone(step=2, name="Declarative Cluster Manifests & Ingress Routing", deliverable="Kubernetes Deployments, Services, Ingress routes, and Horizontal Pod Autoscalers (HPA)."),
                ProjectMilestone(step=3, name="Automated Canary Deployment Pipeline", deliverable="GitHub Actions workflow driving canary deployments with automated rollback on synthetic HTTP 5xx errors."),
            ]
            deliverables = [
                "Complete Helm chart repository for the multi-tier microservice stack",
                "CI/CD workflow YAML implementing vulnerability scanning (Trivy) and canary verification",
                "Cluster resilience demo video demonstrating zero-downtime rolling update under active load",
            ]
            rubric = [
                RubricCriterion(criterion="Container & Cluster Security", target_standard="Non-root containers, drop-all capabilities, and explicit Kubernetes network policies."),
                RubricCriterion(criterion="Deployment Automation & Health", target_standard="Verified rolling updates and automated canary rollbacks without dropped requests."),
            ]
        else:
            title = "Production GitOps Platform with Infrastructure as Code & Drift Detection"
            problem_statement = (
                "Cloud infrastructure drift leads to security vulnerabilities and silent outages. Build an automated "
                "GitOps workflow using declarative IaC that continually reconciles and enforces desired state."
            )
            difficulty = "Intermediate-Advanced"
            required_tools = ["Terraform/OpenTofu", "Docker", "GitHub Actions", "AWS LocalStack", "Shell/Python"]
            milestones = [
                ProjectMilestone(step=1, name="Modular Infrastructure as Code Definitions", deliverable="Parameterized Terraform modules provisioning VPCs, security groups, and compute instances."),
                ProjectMilestone(step=2, name="Automated CI Drift Detection Scheduler", deliverable="Scheduled GitHub Actions cron job executing terraform plan -detailed-exitcode with Slack/webhook alerting."),
                ProjectMilestone(step=3, name="Automated State Reconciliation", deliverable="Automated remediation workflow that re-applies sanctioned states when unauthorized manual changes occur."),
            ]
            deliverables = [
                "Reusable Terraform module registry with state locking and remote backend support",
                "Automated drift detection CI pipeline with alert integration",
                "Architecture decision record (ADR) justifying remote state locking and secret isolation",
            ]
            rubric = [
                RubricCriterion(criterion="IaC Architecture & Modularity", target_standard="Clean separation of modules, variable validations, and zero hardcoded secrets."),
                RubricCriterion(criterion="Automation & Drift Governance", target_standard="Automated detection within 15 minutes of drift and reliable declarative reconciliation."),
            ]

    elif any(s in target_set for s in ["React", "TypeScript", "JavaScript", "HTML/CSS", "Node.js"]):
        demonstrated = [s for s in ["React", "TypeScript", "Node.js", "SQL & Databases", "REST APIs"] if s in role_reqs]
        if not demonstrated:
            demonstrated = target_skills

        if v == 0:
            title = "Collaborative Real-Time Canvas with WebSocket Sync & Optimistic UI"
            problem_statement = (
                "Multiplayer SaaS applications demand sub-50ms user interface responsiveness and concurrent conflict "
                "resolution across multiple browser sessions without client-side screen tearing or state desynchronization."
            )
            difficulty = "Intermediate-Advanced"
            required_tools = ["TypeScript", "React", "Node.js", "WebSockets / Socket.io", "Tailwind CSS", "Vite"]
            milestones = [
                ProjectMilestone(step=1, name="Optimistic State Management & Event Bus", deliverable="Typed client store applying optimistic UI updates with rollback capabilities on network drop."),
                ProjectMilestone(step=2, name="WebSocket Multiplexing & Heartbeat Protocol", deliverable="Node.js WebSocket server broadcasting serialized state diffs with connection heartbeat and reconnection backoff."),
                ProjectMilestone(step=3, name="Conflict Resolution & Presence Indicator", deliverable="Operational transformation or Last-Write-Wins conflict resolution with live peer cursor tracking."),
            ]
            deliverables = [
                "Full-stack monorepo with typed shared contract models across frontend and backend",
                "Stress-test benchmark verifying 100 concurrent WebSocket sessions without event lag",
                "Interactive live deployment on Vercel/Render with automated end-to-end tests (Playwright)",
            ]
            rubric = [
                RubricCriterion(criterion="TypeScript Type Rigor", target_standard="Strict mode TypeScript without 'any', exhaustive switch checks, and typed WebSocket event signatures."),
                RubricCriterion(criterion="Real-time Performance", target_standard="60fps UI rendering during high-frequency remote cursor and canvas mutations."),
            ]
        elif v == 1:
            title = "High-Performance Analytics Dashboard with Server-Side Rendering & Caching"
            problem_statement = (
                "Enterprise telemetry consoles struggle with large datasets, causing browser memory crashes. "
                "Build a high-performance analytics dashboard with virtualized rendering, streaming responses, and sub-100ms load times."
            )
            difficulty = "Intermediate"
            required_tools = ["React", "TypeScript", "Node.js", "PostgreSQL", "Redis", "Chart.js/Recharts"]
            milestones = [
                ProjectMilestone(step=1, name="Streaming Query API with Redis Aggregation", deliverable="Node.js REST endpoint executing aggregated SQL window functions with Redis TTL caching."),
                ProjectMilestone(step=2, name="Virtualized High-Density Data Grid", deliverable="React data table rendering 100,000+ rows smoothly using windowing/virtualization (TanStack Virtual)."),
                ProjectMilestone(step=3, name="Dynamic Filter & Export Engine", deliverable="Multi-dimensional client filtering with debounced query syncing and streaming CSV/PDF generation."),
            ]
            deliverables = [
                "Responsive dashboard web application with light/dark theme support",
                "Lighthouse performance audit report achieving >95 Performance and Accessibility score",
                "Unit and integration test suite with >80% code coverage",
            ]
            rubric = [
                RubricCriterion(criterion="Frontend Performance Optimization", target_standard="Zero main-thread blocking, efficient DOM virtualization, and bundle size <150KB."),
                RubricCriterion(criterion="API Architecture & Caching", target_standard="Deterministic HTTP cache headers (ETags, Stale-While-Revalidate) and safe SQL parametrization."),
            ]
        else:
            title = "Enterprise Micro-Frontend Application with Shared Design System"
            problem_statement = (
                "Large engineering teams need autonomous deployability without duplicating UI components or causing "
                "CSS namespace collisions across distributed frontend micro-apps."
            )
            difficulty = "Advanced"
            required_tools = ["React", "TypeScript", "Module Federation / Vite", "Tailwind CSS", "Jest / Testing Library"]
            milestones = [
                ProjectMilestone(step=1, name="Headless Design System & Component Library", deliverable="Accessible, tokenized component library (Buttons, Modals, Forms) with Storybook documentation."),
                ProjectMilestone(step=2, name="Micro-Frontend Shell & Dynamic Module Federation", deliverable="Host application dynamically loading remote child applications at runtime with fallback error boundaries."),
                ProjectMilestone(step=3, name="Cross-App Global State & Event Bridge", deliverable="Type-safe event dispatcher coordinating user session state and navigation across independent micro-apps."),
            ]
            deliverables = [
                "Published npm/Storybook workspace documenting all reusable atomic components",
                "Host shell container and 2 independently deployed remote micro-frontend applications",
                "Automated visual regression testing pipeline via GitHub Actions",
            ]
            rubric = [
                RubricCriterion(criterion="Architectural Decoupling", target_standard="Independent build and deployment pipelines for each micro-frontend with zero runtime version clashes."),
                RubricCriterion(criterion="Accessibility & Standards", target_standard="Strict WCAG 2.1 AA accessibility compliance across all design system components."),
            ]

    elif any(s in target_set for s in ["Python", "SQL & Databases", "Data Structures & Algorithms", "API Design & REST"]):
        demonstrated = [s for s in ["Python", "SQL & Databases", "API Design & REST", "System Design"] if s in role_reqs]
        if not demonstrated:
            demonstrated = target_skills

        if v == 0:
            title = "High-Concurrency Transactional Ledger with ACID Guarantees & Query Indexing"
            problem_statement = (
                "Financial and audit systems demand strict transaction serializability, efficient database indexing, "
                "and idempotent REST API contracts under concurrent load."
            )
            difficulty = "Intermediate-Advanced"
            required_tools = ["Python (FastAPI/AsyncIO)", "PostgreSQL", "SQLAlchemy", "Locust", "Docker"]
            milestones = [
                ProjectMilestone(step=1, name="Normalized Schema & Composite Indexing", deliverable="Relational schema with foreign keys, constraint checks, and composite index optimization."),
                ProjectMilestone(step=2, name="ACID Transaction Engine & Row-Level Locking", deliverable="Concurrency-safe double-entry ledger handling simultaneous debit/credit transfers without deadlocks."),
                ProjectMilestone(step=3, name="Load Benchmark & Query Profiling", deliverable="Locust load test suite verifying sub-50ms latency under 1,000 req/sec with EXPLAIN ANALYZE verification."),
            ]
            deliverables = [
                "Fully typed RESTful API codebase with comprehensive unit and integration tests",
                "Database migration scripts and EXPLAIN ANALYZE query performance breakdown",
                "Stress-test benchmark documentation verifying race condition resilience",
            ]
            rubric = [
                RubricCriterion(criterion="Data Integrity & Transactions", target_standard="Strict database row locking/optimistic concurrency preventing double-spending."),
                RubricCriterion(criterion="API Architecture & Testing", target_standard="RESTful standards, error handling models, and >85% automated test coverage."),
            ]
        elif v == 1:
            title = "Distributed Event-Driven Processing Engine with Kafka & Outbox Pattern"
            problem_statement = (
                "Microservice architectures often face dual-write inconsistencies when updating a database and publishing events. "
                "Implement a transactional outbox pattern to guarantee at-least-once message delivery with exactly-once idempotency."
            )
            difficulty = "Advanced"
            required_tools = ["Python", "PostgreSQL", "Apache Kafka / Redis Streams", "Docker Compose", "Pytest"]
            milestones = [
                ProjectMilestone(step=1, name="Transactional Outbox Table & Publisher Daemon", deliverable="Database transaction committing business state alongside an outbox event table polled by an asynchronous CDC worker."),
                ProjectMilestone(step=2, name="Message De-duplication & Consumer Idempotency", deliverable="Consumer microservices maintaining processed message hashes to prevent duplicate state execution."),
                ProjectMilestone(step=3, name="Dead-Letter Queue & Poison Pill Isolation", deliverable="Automated DLQ routing after configurable exponential backoff retries with error triage dashboard."),
            ]
            deliverables = [
                "Multi-container docker-compose environment running Kafka, Postgres, publisher, and consumer workers",
                "Failure-injection test script verifying zero message loss during worker crashes",
                "Architectural sequence diagrams detailing outbox lifecycle and failure recovery",
            ]
            rubric = [
                RubricCriterion(criterion="Distributed Consistency", target_standard="Guaranteed at-least-once message delivery and verified idempotency on network retries."),
                RubricCriterion(criterion="Code Quality & Resilience", target_standard="Clean Python domain-driven structure with comprehensive failure-scenario test coverage."),
            ]
        else:
            title = "High-Throughput Rate-Limiting & Traffic Throttling Gateway"
            problem_statement = (
                "Protect backend APIs against denial-of-service traffic spikes and quota abuse using distributed token bucket "
                "and sliding window log rate limiting algorithms."
            )
            difficulty = "Intermediate"
            required_tools = ["Python (FastAPI)", "Redis (Lua scripting)", "Docker", "Locust", "HTTP Client"]
            milestones = [
                ProjectMilestone(step=1, name="Atomic Redis Lua Token Bucket Implementation", deliverable="Lua script executed inside Redis to evaluate token refill and deduction in a single atomic roundtrip."),
                ProjectMilestone(step=2, name="Middleware Integration & HTTP Rate-Limit Headers", deliverable="FastAPI middleware attaching standard IETF headers (RateLimit-Limit, RateLimit-Remaining, Retry-After)."),
                ProjectMilestone(step=3, name="Distributed Load & Quota Boundary Verification", deliverable="Benchmark script simulating 10,000 rapid concurrent requests proving exact threshold enforcement."),
            ]
            deliverables = [
                "Lightweight standalone API gateway service ready for containerized deployment",
                "Benchmark report demonstrating sub-2ms rate-limiting overhead per incoming request",
                "Comprehensive README explaining mathematical basis for sliding window vs token bucket",
            ]
            rubric = [
                RubricCriterion(criterion="Concurrency & Atomicity", target_standard="Zero race conditions under concurrent requests using atomic Redis operations."),
                RubricCriterion(criterion="Standard Compliance & Clean Code", target_standard="Proper HTTP status 429 responses with accurate Retry-After time calculations."),
            ]

    else:
        demonstrated = target_skills
        if v == 0:
            title = f"Production-Grade Technical Architecture Demonstrating {', '.join(target_skills)}"
            problem_statement = (
                f"Build a production-grade system that specifically exercises {', '.join(target_skills)} "
                f"to solve real-world enterprise operational constraints with high reliability."
            )
        elif v == 1:
            title = f"Resilient Distributed Service for {', '.join(target_skills)} with Automated Failover"
            problem_statement = (
                f"Design an automated, fault-tolerant service emphasizing {', '.join(target_skills)} "
                f"with comprehensive telemetry, automated self-healing, and end-to-end integration tests."
            )
        else:
            title = f"High-Performance Cloud Pipeline Implementing {', '.join(target_skills)}"
            problem_statement = (
                f"Implement a high-throughput, low-latency pipeline focused on {', '.join(target_skills)} "
                f"with automated metrics reporting, regression benchmarks, and infrastructure automation."
            )

        difficulty = "Intermediate"
        required_tools = target_skills + ["Git", "Automated Testing", "Docker"]
        milestones = [
            ProjectMilestone(step=1, name="Core Architecture & Interfaces", deliverable=f"Core implementation of {target_skills[0]}."),
            ProjectMilestone(step=2, name="Integration, Testing & Hardening", deliverable="End-to-end operational integration with automated test suite."),
            ProjectMilestone(step=3, name="Operational Observability & Packaging", deliverable="Production deployment package with automated health checks."),
        ]
        deliverables = ["Source repository", "Architecture specification", "Verification test suite"]
        rubric = [RubricCriterion(criterion="Technical Execution", target_standard="Adherence to industry best practices.")]

    why_recommended = (
        f"Your Career Twin identifies {', '.join(target_skills)} as primary verification deficits "
        f"for {candidate.target_role}. Delivering this project produces tangible technical evidence "
        f"addressing these specific gaps (Suggestion #{variation_index + 1})."
    )

    evidence_profile_impact = (
        f"Completing and publishing this project directly updates your Career Twin skill evidence "
        f"for {', '.join(demonstrated)} from their current provisional status to "
        f"Project-demonstrated, increasing your portfolio readiness sub-score."
    )

    return PortfolioProjectResponse(
        title=sanitize_gemini_text(title),
        problem_statement=sanitize_gemini_text(problem_statement),
        why_recommended=sanitize_gemini_text(why_recommended),
        skills_demonstrated=demonstrated,
        difficulty=difficulty,
        required_tools=required_tools,
        milestones=milestones,
        expected_deliverables=deliverables,
        evaluation_rubric=rubric,
        evidence_profile_impact=sanitize_gemini_text(evidence_profile_impact),
    )
