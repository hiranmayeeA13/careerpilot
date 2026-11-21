import re
import uuid
from typing import Dict, List, Optional
from app.database import get_candidate
from app.models.schemas import (
    CandidateProfile,
    InterviewQuestion,
    InterviewStartResponse,
    InterviewSubmitRequest,
    InterviewSubmitResponse,
    QuestionScore,
)
from app.services.job_market_service import build_skill_gap_map
from app.services.twin_service import update_career_twin

QUESTION_BANK: Dict[str, List[Dict]] = {
    "Linux": [
        {
            "question": "Walk me through how you'd diagnose a Linux server that's running out of memory.",
            "rubric": ["mentions monitoring commands (top/htop/free/vmstat)", "mentions process identification (ps/kill/oom)", "mentions logs (/var/log, dmesg, journalctl)", "mentions a concrete remediation step (cgroup limits, swap, scale)"],
            "keywords": [["top", "htop", "free", "vmstat"], ["ps", "kill", "oom"], ["log", "dmesg", "journalctl"], ["restart", "scale", "limit", "cgroup", "swap"]],
        },
        {
            "question": "How do Linux permissions, systemd service units, and security boundaries isolate production daemons?",
            "rubric": ["mentions chmod/chown and least-privilege users", "mentions systemd unit files & restart policies", "mentions security capabilities (ProtectSystem, NoNewPrivileges)", "mentions logging via journalctl"],
            "keywords": [["chmod", "chown", "permission", "privilege"], ["systemd", "service", "unit", "restart"], ["user", "group", "protect", "isolate", "capability"], ["journalctl", "log", "status"]],
        },
        {
            "question": "Explain Linux CPU load averages and how to distinguish between CPU saturation and disk I/O bottlenecks.",
            "rubric": ["explains 1, 5, 15 minute exponential load averages", "mentions vmstat/iostat for I/O wait identification", "mentions context switching or run-queue depth", "mentions root cause mitigation"],
            "keywords": [["average", "load", "minute"], ["iowait", "vmstat", "iostat", "io"], ["cpu", "context", "run queue", "thread"], ["disk", "df", "throughput", "bottleneck"]],
        },
    ],
    "Networking": [
        {
            "question": "Explain what happens, step by step, when a browser loads a website (DNS to TCP to HTTP).",
            "rubric": ["mentions DNS resolution & caching", "mentions TCP 3-way handshake (SYN, SYN-ACK, ACK)", "mentions TLS/SSL negotiation", "mentions HTTP request/response headers & lifecycle"],
            "keywords": [["dns", "resolve", "ip"], ["tcp", "handshake", "syn", "ack"], ["tls", "ssl", "https", "handshake", "certificate"], ["http", "request", "response", "status"]],
        },
        {
            "question": "How does CIDR subnetting, NAT, and gateway routing direct traffic between private and public subnets?",
            "rubric": ["mentions CIDR notation & subnet masks", "mentions private vs public IP ranges (RFC 1918)", "mentions NAT gateways for outbound internet access", "mentions route tables and default 0.0.0.0/0 route"],
            "keywords": [["cidr", "subnet", "mask", "/24"], ["private", "public", "ip", "10.", "192."], ["nat", "gateway", "outbound"], ["route", "table", "hop"]],
        },
        {
            "question": "How do you troubleshoot high packet loss or connection timeouts between distributed microservices?",
            "rubric": ["mentions ping, traceroute, or mtr", "mentions netcat, curl, or telnet for port connectivity", "mentions tcpdump/Wireshark packet capture", "mentions firewall/security group inspection"],
            "keywords": [["ping", "traceroute", "mtr"], ["netcat", "curl", "telnet", "port"], ["tcpdump", "wireshark", "packet"], ["firewall", "iptables", "security group"]],
        },
    ],
    "Docker": [
        {
            "question": "How would you reduce the size and build time of a Docker image for a web service?",
            "rubric": ["mentions multi-stage builds", "mentions slim/alpine minimal base images", "mentions layer caching optimization", "mentions .dockerignore or cleaning build artifacts"],
            "keywords": [["multi-stage", "multi stage"], ["slim", "alpine", "distroless"], ["cache", "layer", "order"], ["dockerignore", "prune", "clean", "artifact"]],
        },
        {
            "question": "Explain Docker networking modes (bridge, host, overlay) and how containers communicate safely.",
            "rubric": ["mentions default bridge network & port mapping", "mentions host networking trade-offs", "mentions overlay/custom user-defined bridge networks", "mentions internal DNS service discovery"],
            "keywords": [["bridge", "network"], ["host", "performance"], ["overlay", "custom", "swarm"], ["dns", "resolve", "name", "communicate"]],
        },
        {
            "question": "How do you secure containers in production against privilege escalation and breakout attacks?",
            "rubric": ["mentions running as non-root user (USER directive)", "mentions read-only root filesystems", "mentions dropping Linux capabilities (cap-drop)", "mentions image vulnerability scanning (Trivy/Clair)"],
            "keywords": [["root", "user", "non-root"], ["read-only", "filesystem", "volume"], ["cap-drop", "capability", "privilege"], ["scan", "vulnerability", "trivy", "cve"]],
        },
    ],
    "Kubernetes": [
        {
            "question": "A pod keeps crash-looping in Kubernetes. Walk through your step-by-step debugging workflow.",
            "rubric": ["mentions kubectl describe pod and reading events", "mentions kubectl logs (including --previous)", "mentions resource limits/requests & OOMKilled checks", "mentions liveness/readiness probe misconfigurations"],
            "keywords": [["describe", "kubectl describe", "events"], ["logs", "previous", "stdout"], ["oom", "limit", "request", "memory"], ["probe", "liveness", "readiness", "health"]],
        },
        {
            "question": "How do Ingress controllers, Services (ClusterIP/NodePort), and Pods route incoming external traffic?",
            "rubric": ["mentions Ingress controller & TLS termination", "mentions ClusterIP vs NodePort vs LoadBalancer", "mentions endpoints and kube-proxy / iptables routing", "mentions selector matching labels to pods"],
            "keywords": [["ingress", "host", "path", "tls"], ["clusterip", "nodeport", "loadbalancer"], ["endpoint", "kube-proxy", "iptables"], ["selector", "label", "pod"]],
        },
        {
            "question": "Explain Kubernetes zero-downtime rolling updates and how PodDisruptionBudgets protect availability.",
            "rubric": ["mentions RollingUpdate strategy (maxSurge / maxUnavailable)", "mentions readiness probe gating traffic switchover", "mentions PodDisruptionBudget (PDB) during node drains", "mentions graceful termination (preStop hook / SIGTERM)"],
            "keywords": [["rolling", "surge", "unavailable"], ["readiness", "probe", "traffic"], ["pdb", "poddisruptionbudget", "drain"], ["sigterm", "prestop", "graceful", "terminate"]],
        },
    ],
    "CI/CD": [
        {
            "question": "Design a resilient CI/CD pipeline for a web service from Git commit to production release.",
            "rubric": ["mentions automated linting and unit/integration testing", "mentions immutable artifact/container build & scanning", "mentions environment progression (staging to production)", "mentions automated rollback strategies"],
            "keywords": [["test", "unit", "lint", "ci"], ["artifact", "image", "build", "immutable"], ["staging", "production", "environment"], ["rollback", "canary", "blue-green"]],
        },
        {
            "question": "Explain blue-green deployments versus canary releases and how traffic routing is managed.",
            "rubric": ["defines blue-green deployment (two identical environments)", "defines canary deployment (gradual % traffic rollout)", "mentions routing mechanisms (load balancer, ingress, feature flags)", "mentions observability and automated abort triggers"],
            "keywords": [["blue-green", "blue green", "switch"], ["canary", "percentage", "gradual"], ["router", "ingress", "traffic", "load balancer"], ["metrics", "abort", "rollback", "error rate"]],
        },
        {
            "question": "How do you manage secrets, credential rotation, and supply chain security in CI/CD runners?",
            "rubric": ["mentions secret managers / OIDC tokens rather than hardcoded credentials", "mentions ephemeral or isolated runners", "mentions dependency lockfiles & software bill of materials (SBOM)", "mentions automated credential rotation"],
            "keywords": [["secret", "vault", "oidc", "kms"], ["runner", "ephemeral", "isolated"], ["lockfile", "sbom", "dependency", "audit"], ["rotate", "rotation", "expire"]],
        },
    ],
    "Python": [
        {
            "question": "How do you handle processing multi-gigabyte data files in Python without exhausting system RAM?",
            "rubric": ["mentions generators and yield for lazy evaluation", "mentions streaming line-by-line or chunked processing", "mentions memory profiling or garbage collection", "mentions concrete libraries (itertools, pandas chunksize)"],
            "keywords": [["generator", "yield", "lazy"], ["stream", "chunk", "line"], ["memory", "profile", "ram", "garbage"], ["itertools", "pandas", "chunksize"]],
        },
        {
            "question": "Explain Python's Global Interpreter Lock (GIL), when it matters, and how to bypass it for CPU-heavy tasks.",
            "rubric": ["explains GIL restricts execution to one native thread at a time", "identifies I/O-bound tasks benefit from threading/asyncio", "identifies CPU-bound tasks require multiprocessing or C extensions", "mentions modern developments (free-threaded Python 3.13)"],
            "keywords": [["gil", "global interpreter lock", "thread"], ["io", "asyncio", "threading", "network"], ["multiprocessing", "process", "cpu", "cores"], ["python 3.13", "c extension", "parallel"]],
        },
        {
            "question": "How does Python's asyncio event loop operate under the hood, and how do you prevent blocking it?",
            "rubric": ["explains single-threaded cooperative multitasking event loop", "mentions await points yielding control to the scheduler", "warns against synchronous blocking calls (time.sleep, synchronous requests)", "mentions running blocking code via run_in_executor"],
            "keywords": [["event loop", "asyncio", "cooperative"], ["await", "yield", "coroutine"], ["blocking", "synchronous", "freeze"], ["executor", "run_in_executor", "threadpool"]],
        },
    ],
    "React": [
        {
            "question": "How does React's reconciliation algorithm and Virtual DOM diffing achieve efficient UI updates?",
            "rubric": ["mentions Virtual DOM tree comparison", "mentions key prop importance for list element identity", "mentions fiber architecture and priority scheduling", "mentions batching state updates"],
            "keywords": [["virtual dom", "diff", "reconciliation"], ["key", "identity", "list"], ["fiber", "render", "tree"], ["batch", "batching", "state"]],
        },
        {
            "question": "How do you optimize a React application suffering from frequent unnecessary component re-renders?",
            "rubric": ["mentions React.memo for pure functional components", "mentions useMemo and useCallback for referential stability", "mentions state colocation / lifting state down", "mentions React DevTools Profiler to measure renders"],
            "keywords": [["memo", "react.memo"], ["usememo", "usecallback", "reference"], ["colocation", "lift", "state"], ["profiler", "devtools", "measure"]],
        },
        {
            "question": "Explain custom React hooks design: rules, composition, and cleanup in useEffect.",
            "rubric": ["mentions extracting reusable stateful logic", "mentions Rules of Hooks (top-level only, call from React functions)", "mentions useEffect dependency array correctness", "mentions cleanup functions for subscriptions/timers"],
            "keywords": [["custom hook", "reusable", "logic"], ["rules of hooks", "top-level", "condition"], ["dependency", "dependencies", "array"], ["cleanup", "unsubscribe", "unmount"]],
        },
    ],
    "TypeScript": [
        {
            "question": "How do Generics, conditional types, and utility types (Pick, Omit, Partial) build robust type contracts in TypeScript?",
            "rubric": ["explains type parametrization using generics", "explains conditional type syntax (T extends U ? X : Y)", "mentions standard utility types (Partial, Pick, Omit)", "mentions compile-time type safety without runtime overhead"],
            "keywords": [["generic", "type parameter", "<t>"], ["conditional", "extends", "ternary"], ["pick", "omit", "partial", "record"], ["compile", "runtime", "safety"]],
        },
        {
            "question": "Explain type narrowing, discriminated unions, and custom type guards (is operator).",
            "rubric": ["defines discriminated union with common literal property", "explains typeof / instanceof / in checks", "demonstrates custom type guard syntax (val is TargetType)", "explains exhaustiveness checking with never type"],
            "keywords": [["discriminated union", "tag", "literal"], ["narrowing", "typeof", "instanceof"], ["type guard", "is", "predicate"], ["never", "exhaustive", "switch"]],
        },
        {
            "question": "What is the difference between type aliases and interfaces, and when should each be preferred?",
            "rubric": ["mentions interface declaration merging", "mentions type alias support for unions, primitives, and tuples", "mentions extends / implements object modeling", "mentions team consistency and performance best practices"],
            "keywords": [["interface", "merging", "declaration"], ["type", "union", "primitive", "tuple"], ["extends", "implements", "class"], ["performance", "clean", "consistent"]],
        },
    ],
    "Node.js": [
        {
            "question": "Walk through Node.js event loop phases (timers, I/O polling, check) and process.nextTick priority.",
            "rubric": ["mentions libuv event loop architecture", "mentions timers phase (setTimeout/setInterval)", "mentions I/O poll and check phase (setImmediate)", "mentions microtask queue priority (nextTick / Promises)"],
            "keywords": [["libuv", "event loop"], ["timers", "timeout"], ["poll", "setimmediate", "check"], ["nexttick", "microtask", "promise"]],
        },
        {
            "question": "How do Node.js Streams work, and why are they critical for high-throughput network applications?",
            "rubric": ["mentions readable, writable, duplex, and transform streams", "mentions backpressure handling", "mentions memory efficiency piping data chunks", "mentions pipeline utility and error handling"],
            "keywords": [["stream", "readable", "writable", "duplex"], ["backpressure", "buffer"], ["pipe", "pipeline", "chunk"], ["error", "leak", "memory"]],
        },
        {
            "question": "How do you detect, profile, and fix memory leaks in production Node.js microservices?",
            "rubric": ["mentions heap snapshot generation via v8 or Chrome DevTools", "mentions identifying common causes (closures, global variables, event listeners)", "mentions garbage collection tracking (--inspect)", "mentions automated container health probes and graceful restart"],
            "keywords": [["heap", "snapshot", "v8"], ["closure", "event listener", "leak", "global"], ["garbage collection", "gc", "inspect"], ["restart", "memory limit", "profile"]],
        },
    ],
    "SQL & Databases": [
        {
            "question": "A slow database query is taking several seconds on a multi-million-row table. Walk through your optimization strategy.",
            "rubric": ["mentions EXPLAIN / EXPLAIN ANALYZE query plan execution", "mentions B-tree indexing on filter/join columns", "mentions avoiding SELECT * and unnecessary joins", "mentions schema optimization or caching layers (Redis)"],
            "keywords": [["explain", "analyze", "query plan"], ["index", "b-tree", "composite"], ["select", "join", "filter"], ["cache", "redis", "schema"]],
        },
        {
            "question": "Explain database transaction isolation levels (Read Uncommitted up to Serializable) and the concurrency anomalies they prevent.",
            "rubric": ["defines Dirty Reads, Non-Repeatable Reads, and Phantom Reads", "explains Read Committed as common default", "explains Repeatable Read snapshot isolation", "explains Serializable and MVCC / lock overhead trade-offs"],
            "keywords": [["dirty read", "phantom", "non-repeatable"], ["read committed", "default"], ["repeatable read", "snapshot"], ["serializable", "mvcc", "lock"]],
        },
        {
            "question": "How does database sharding, read-replicas, and connection pooling scale high-volume write and read traffic?",
            "rubric": ["explains master-replica topology for read scaling", "explains sharding / partition keys for horizontal write scaling", "mentions connection poolers (PgBouncer) preventing connection overhead", "mentions replication lag handling"],
            "keywords": [["replica", "read", "primary", "master"], ["shard", "partition", "horizontal"], ["pgbouncer", "pool", "connection"], ["lag", "eventual consistency"]],
        },
    ],
    "System Design": [
        {
            "question": "How would you design a distributed, high-concurrency URL shortener capable of handling millions of requests daily?",
            "rubric": ["mentions unique ID generation (Snowflake, Base62 hashing)", "mentions database schema and key-value/NoSQL storage", "mentions multi-level caching (Redis / CDN) for read speed", "mentions horizontal load balancing and rate limiting"],
            "keywords": [["hash", "base62", "id", "snowflake"], ["database", "nosql", "key-value", "store"], ["cache", "redis", "cdn"], ["load balancer", "rate limit", "horizontal"]],
        },
        {
            "question": "Design a resilient notifications system that sends millions of transactional emails and SMS reliably without dropping messages.",
            "rubric": ["mentions message queues (Kafka, RabbitMQ, SQS) for asynchronous buffering", "mentions worker consumer pools and concurrency scaling", "mentions retry policies with exponential backoff and dead-letter queues (DLQ)", "mentions idempotency keys preventing duplicate alerts"],
            "keywords": [["queue", "kafka", "rabbitmq", "sqs"], ["worker", "consumer", "async"], ["retry", "backoff", "dlq", "dead letter"], ["idempotency", "duplicate", "dedup"]],
        },
        {
            "question": "Explain the CAP theorem and describe how you make consistency vs availability trade-offs in distributed systems.",
            "rubric": ["defines Consistency, Availability, and Partition Tolerance", "explains network partitions are inevitable in distributed systems", "contrasts CP systems (e.g. Raft, Paxos, strict databases) with AP systems (e.g. Cassandra, Dynamo)", "mentions eventual consistency and PACELC theorem"],
            "keywords": [["cap theorem", "partition"], ["consistency", "availability"], ["cp", "ap", "raft", "paxos", "dynamo"], ["eventual consistency", "pacelc", "tradeoff"]],
        },
    ],
}

DEFAULT_QUESTIONS = [
    {
        "question": "Walk me through the architecture of a complex system you engineered, highlighting the core design decisions and trade-offs.",
        "rubric": ["articulates clear system architecture & component boundaries", "justifies technical choices against concrete requirements", "discusses trade-offs considered (latency, cost, complexity)", "describes verification and operational monitoring"],
        "keywords": [["architecture", "design", "component"], ["requirement", "scale", "decision"], ["trade-off", "tradeoff", "alternative", "latency"], ["monitor", "metric", "test", "production"]],
    },
    {
        "question": "Describe a difficult production outage or subtle technical bug you debugged. How did you isolate root cause and remediate it?",
        "rubric": ["describes symptom detection and triage strategy", "explains systematic root-cause isolation workflow", "details concrete immediate remediation & permanent architectural fix", "mentions postmortem and preventative observability improvements"],
        "keywords": [["outage", "bug", "incident", "failure"], ["isolate", "root cause", "debug", "trace"], ["fix", "remediate", "deploy", "patch"], ["postmortem", "prevent", "alert", "monitor"]],
    },
    {
        "question": "How do you evaluate performance bottlenecks, resource saturation, and scalability limits when optimizing critical services?",
        "rubric": ["identifies profiling methodologies and bottleneck metrics (CPU, memory, I/O)", "mentions benchmark and stress-testing under load", "explains algorithmic or architectural optimizations implemented", "validates measurable performance gains with concrete numbers"],
        "keywords": [["profile", "bottleneck", "metric", "latency"], ["load test", "benchmark", "stress"], ["optimize", "cache", "algorithm", "concurrency"], ["throughput", "gain", "reduced", "faster"]],
    },
]


def generate_mock_interview(candidate: CandidateProfile, variant: int = 0) -> InterviewStartResponse:
    gap_map = build_skill_gap_map(candidate)
    weak_skills = [r.skill for r in gap_map.requirements if not r.is_met][:4]
    if not weak_skills:
        weak_skills = list(candidate.skills.keys())[:3] or ["General Architecture"]

    session_id = f"sess_{uuid.uuid4().hex[:10]}"
    questions: List[InterviewQuestion] = []

    for skill in weak_skills:
        options = QUESTION_BANK.get(skill)
        if options:
            selected = options[variant % len(options)]
        else:
            selected = DEFAULT_QUESTIONS[variant % len(DEFAULT_QUESTIONS)]

        # Hex-encode the skill name and pack variant so decode is 100% loss-free
        hex_skill = skill.encode("utf-8").hex()
        q_id = f"{session_id}__v{variant}__{hex_skill}"

        questions.append(
            InterviewQuestion(
                question_id=q_id,
                skill=skill,
                question=selected["question"],
                rubric=selected["rubric"],
            )
        )

    return InterviewStartResponse(session_id=session_id, candidate_id=candidate.id, questions=questions)


def _score_answer(skill: str, answer_text: str, variant: int = 0) -> QuestionScore:
    options = QUESTION_BANK.get(skill)
    if options:
        bank = options[variant % len(options)]
    else:
        bank = DEFAULT_QUESTIONS[variant % len(DEFAULT_QUESTIONS)]

    lowered = answer_text.lower()
    hits, misses = [], []

    for criterion, keyword_group in zip(bank["rubric"], bank["keywords"]):
        matched = any(re.search(r"\b" + re.escape(kw) + r"\b", lowered) or kw in lowered for kw in keyword_group)
        (hits if matched else misses).append(criterion)

    rubric_score = round(100 * len(hits) / max(1, len(bank["rubric"])))

    # Depth & Technical substance analysis
    words = [w for w in re.split(r"\s+", answer_text.strip()) if w]
    word_count = len(words)

    # Check for structural reasoning markers
    structure_markers = ["because", "therefore", "trade-off", "tradeoff", "alternatively", "implemented", "configured", "monitored", "architecture", "optimized"]
    structure_hits = sum(1 for m in structure_markers if m in lowered)

    # Length & substance adjustments
    if word_count < 10:
        length_adj = -25
    elif word_count < 25:
        length_adj = -10
    elif word_count >= 50:
        length_adj = 5
    elif word_count >= 80:
        length_adj = 10
    else:
        length_adj = 0

    structure_bonus = min(10, structure_hits * 3)
    final_score = max(0, min(100, rubric_score + length_adj + structure_bonus))

    if final_score >= 80:
        feedback = f"Outstanding technical answer! You demonstrated solid command of {skill}, covering core principles and actionable trade-offs."
    elif final_score >= 55:
        feedback = f"Good foundational explanation for {skill}. To reach the highest scoring tier, incorporate more concrete metrics, tool configurations, and failure handling."
    else:
        feedback = f"Answer was brief or lacked specific technical depth for {skill}. Review the rubric criteria below to touch upon the key operational concepts expected in interviews."

    return QuestionScore(
        question_id="",
        skill=skill,
        score=final_score,
        rubric_hits=hits,
        rubric_misses=misses,
        feedback=feedback,
    )


def submit_mock_interview(request: InterviewSubmitRequest) -> InterviewSubmitResponse:
    candidate = get_candidate(request.candidate_id)
    if not candidate:
        raise ValueError(f"Candidate '{request.candidate_id}' not found")

    per_question: List[QuestionScore] = []
    skills_covered: List[str] = []

    for ans in request.answers:
        q_id = ans.question_id
        skill = "General"
        variant = 0

        # Parse robust encoding: session__v{variant}__{hex_skill}
        if "__v" in q_id and q_id.count("__") >= 2:
            parts = q_id.split("__")
            try:
                v_part = parts[1]
                if v_part.startswith("v"):
                    variant = int(v_part[1:])
                hex_part = parts[2]
                skill = bytes.fromhex(hex_part).decode("utf-8")
            except Exception:
                skill = parts[-1].replace("_", " ")
        elif "_" in q_id:
            # Fallback for old question_id pattern
            skill_slug = q_id.rsplit("_", 1)[-1]
            skill = skill_slug.replace("_", " ")

        scored = _score_answer(skill, ans.answer_text, variant=variant)
        scored.question_id = ans.question_id
        per_question.append(scored)
        skills_covered.append(skill)

    overall = round(sum(q.score for q in per_question) / max(1, len(per_question)))

    recorded = False
    plan_adjusted = False
    try:
        update_career_twin(
            candidate_id=request.candidate_id,
            trigger_type="interview_completed",
            payload={
                "interview_id": request.session_id,
                "target_role": candidate.target_role,
                "performance_score": overall,
                "skills_evaluated": skills_covered,
                "feedback": f"Mock interview completed — {len(per_question)} question(s) evaluated, score {overall}/100.",
            },
        )
        recorded = True
        plan_adjusted = True
    except Exception:
        pass

    return InterviewSubmitResponse(
        overall_score=overall,
        per_question=per_question,
        recorded_to_career_twin=recorded,
        plan_adjusted=plan_adjusted,
    )
