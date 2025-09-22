# Multi‑Agent System Patterns — Full Reference
_Date: 07 August 2025_

This reference supports engineers who design and operate domain‑agnostic multi‑agent platforms. It outlines patterns, forces, and operational guidance in a compact, skimmable format. Each pattern entry includes: Summary → Problem → Forces → Solution (with a small ASCII diagram) → Implementation Notes → Variations → Benefits & Trade‑offs → Example → Operational Checklist → Related Patterns → Anti‑Patterns to Avoid → When to Use.

---

# 0  Introduction — The Platform Mindset

Think infrastructure first: registry, messaging, context, lifecycle. Agents remain simple and focused; the platform handles discovery, transport, and shared memory. Build with a **minimal core** (registry, message transport, lifecycle) and grow capabilities via modular patterns. Start with the smallest viable infrastructure, measure, and iterate.

---

# 1  Foundation Patterns

## 1.1  Agent Registry Pattern
Tags : mature · medium‑complexity · required

**Summary**  
Catalogue where agents register identity and capabilities and discover peers at runtime.

### Problem
Hard‑coded endpoints create fragility, block evolution, and magnify failure blast radius.

### Forces
Flexibility ↔ simplicity; availability ↔ consistency; semantic matching ↔ strict schemas; low latency ↔ rich queries.

### Solution
```
Agent ──register()/update()──▶ Registry ◀──discover(by capability)── Agent
                              ▲ evict on health‑fail
```
Core ops: Register · Discover · Update · Health · Deregister.

### Implementation Notes
- Storage: KV (Redis/etcd), Document (MongoDB/DynamoDB), Graph (Neo4j/Neptune).  
- Discovery: well‑known address, DNS‑SRV, config‑injection, limited broadcast.  
- Capability schema (YAML): type, domains, constraints, endpoint, health, version.  
- Security: mTLS, signed manifests, RBAC on queries.  
- Performance: target p50 lookup < 10 ms in‑cluster; replicate when p95 creeps > 50 ms.

### Variations
Hierarchical registry · Capability broker · Gossip‑based self‑organising registry.

### Benefits & Trade‑offs
+ Dynamic composition; capability‑based discovery; central observability.  
− Extra infrastructure; lookup overhead; eventual consistency; attack surface.

### Example
Add **Translation Agent**; existing **Report Agent** discovers it and produces French output without code change.

### Operational Checklist
Prune stale entries; backup state; alert on query latency and stale‑count; rotate keys.

### Related Patterns
Requires **1.2 Message Transport** · Enables **5.5 Capability Discovery**.

### Anti‑Patterns to Avoid
Static fallbacks; over‑specified capabilities; turning registry into an orchestrator.

### When to Use
> 3 agents, multi‑team development, rolling evolution, heterogeneous lifespans.

---

## 1.2  Message Transport Pattern
Tags : mature · low‑complexity · required

**Summary**  
Shared queue/bus/stream moves envelopes with acknowledgements and retries for decoupled, reliable messaging.

### Problem
Ad‑hoc HTTP or sockets diverge in schema and retry logic; outages cascade; back‑pressure melts workflows.

### Forces
Throughput ↔ latency; loose coupling ↔ delivery guarantees; version stability ↔ schema evolution; encryption cost ↔ speed.

### Solution
```
Agent X ──envelope──▶  Queue/Topic  ──deliver──▶ Agent Y
            ▲ ack/retry                          ▲ dead‑letter on fail
```
Core ops: Send · Receive · Ack/Retry · Dead‑letter · Broadcast.

### Implementation Notes
- Options: NATS/RabbitMQ/SQS (at‑least‑once); Kafka/Pulsar (high throughput); gRPC/HTTP (proto).  
- Envelope: type, schema version, correlation/trace‑ID, optional signature.  
- QoS: at‑least‑once for idempotent handlers; exactly‑once only when stateful side‑effects demand it.  
- Security: mTLS; signed envelopes; topic RBAC; publish rate‑limits.  
- Performance: aim p50 enqueue→dequeue < 10 ms in‑cluster; load‑test at 4× peak.

### Variations
In‑process channel · HTTP pull model · Segmented bus (critical vs analytics topics).

### Benefits & Trade‑offs
+ Decouples lifecycles; uniform tracing; burst absorption.  
− Extra hop latency; broker operations; SPOF unless clustered.

### Example
X publishes `build.complete` to `build‑events`; Y handles and emits audit to `audit‑events` within budget.

### Operational Checklist
Monitor queue depth, consumer lag, dead‑letter rate; rotate certs; manage retention windows.

### Related Patterns
Works with **2.2.2 Publish‑Subscribe** · Required by **1.1 Agent Registry**.

### Anti‑Patterns to Avoid
Single huge topic; unbounded fan‑out; silent drop of unroutables.

### When to Use
As soon as ≥ 2 agents require asynchronous coordination; avoid for one synchronous pair.

---

## 1.3  Agent Lifecycle Management Pattern
Tags : mature · medium‑complexity

**Summary**  
Standard hooks for create, start, pause, resume, scale, and retire agents under supervision.

### Problem
Without consistent lifecycle hooks, restart storms, leaked work, and zombie agents accumulate.

### Forces
Fast restarts ↔ graceful draining; autonomy ↔ central supervision; scaling speed ↔ warm‑up readiness.

### Solution
```
Supervisor ◀─heartbeats/health── Agent
   │ spawn/scale/retire
   └─▶ State store (assignments, checkpoints)
```
Core ops: Spawn · Register · Heartbeat · Drain · Snapshot · Retire · Replace.

### Implementation Notes
Supervisors/watchdogs; grace periods; idempotent shutdown; checkpointing; failure budgets; rolling restarts.

### Variations
Stateless workers with leases · Warm pools for rapid scale‑up · Canary lifecycles.

### Benefits & Trade‑offs
+ Predictable restarts; safer upgrades; audit of lifecycle events.  
− More moving parts; careful tuning required for drains and leases.

### Example
Supervisor detects failed heartbeat, drains tasks, spawns a replacement, and replays from last checkpoint.

### Operational Checklist
Alert on repeated restarts; track MTTD/MTTR; audit lifecycle logs; cap concurrency during scale‑down.

### Related Patterns
Interacts with **8.1 Resilient Communication** · Depends on **1.1 Registry** for identification.

### Anti‑Patterns to Avoid
Kill‑9 without drain; unbounded retries; mixing lifecycle with business logic.

### When to Use
Multi‑node deployments, bursty workloads, or any environment needing safe rolling updates.

---

# 2  Communication Patterns

## 2.1.1  Request‑Reply Pattern
Tags : mature · low‑complexity · synchronous

**Summary**  
Simple synchronous query‑response between agents.

### Problem
Blocking calls can stall pipelines and amplify failures.

### Forces
Low latency ↔ robustness; synchronous simplicity ↔ back‑pressure; retries ↔ idempotency.

### Solution
```
Caller ──request──▶ Callee ──reply──▶ Caller
         timeout/circuit‑breakers
```
Core ops: Request · Response · Timeout · Retry.

### Implementation Notes
Set timeouts; circuit breakers; idempotent handlers; exponential backoff; small payloads.

### Variations
Batching; streaming responses; duplex RPC.

### Benefits & Trade‑offs
+ Straightforward semantics.  
− Head‑of‑line blocking; tight coupling to callee availability.

### Example
Planner requests price quote; times out after 300 ms and falls back.

### Operational Checklist
Track p95 latency; timeout ratios; failure reasons; retry budgets.

### Related Patterns
Use **8.4 Version Negotiation**; consider **2.3.2 EDA** for async alternatives.

### Anti‑Patterns
Endless waits; synchronous fan‑out; long‑running tasks inline.

### When to Use
Low‑latency reads or control paths with bounded work.

---

## 2.1.2  Agent‑to‑Agent (A2A) Protocol
Tags : emerging · medium‑complexity · standardised

**Summary**  
Shared schema/handshake for direct agent interactions with capability negotiation.

### Problem
Heterogeneous agents struggle to interoperate without a common contract.

### Forces
Interoperability ↔ velocity; strict types ↔ flexibility; evolution ↔ stability.

### Solution
```
A ──hello+versions/capabilities──▶ B
A ◀──accept+contract────────────── B
```
Core ops: Hello · Version/Feature negotiation · AuthN/AuthZ · Error taxonomy.

### Implementation Notes
Signed messages; schema registry; consistent error codes; deprecation policy.

### Variations
Binary vs JSON; out‑of‑band capability discovery via **1.1 Registry**.

### Benefits & Trade‑offs
+ Predictable interop; simplifies tooling.  
− Upfront design costs; version management.

### Example
A2A negotiates `search.v2`; older `v1` falls back until deprecation window closes.

### Operational Checklist
Track version adoption; reject unknown features; lint contracts in CI.

### Related Patterns
Leans on **8.6 Standardised Message Format**.

### Anti‑Patterns
Implicit contracts; silent feature drift.

### When to Use
Cross‑team or cross‑language agent meshes.

---

## 2.2.1  Blackboard Pattern
Tags : mature · medium‑complexity · collaborative

**Summary**  
Shared workspace where agents post partial solutions and observe updates.

### Problem
Complex problems need incremental, multi‑specialist contributions.

### Forces
Visibility ↔ contention; freshness ↔ cost; openness ↔ security.

### Solution
```
Agents ◀──read/observe── Blackboard ──post/update── Agents
           conflict‑resolution + TTL
```
Core ops: Post · Observe · Merge · Expire.

### Implementation Notes
CRDTs or optimistic locking; TTL/GC; subscription filters; provenance fields.

### Variations
Topic‑segmented blackboards; privacy‑scoped boards.

### Benefits & Trade‑offs
+ Encourages collaboration; decouples timing.  
− Requires strong consistency rules and clean‑up.

### Example
Vision and Planner post alternately to converge on a plan.

### Operational Checklist
Monitor contention, merge conflicts, and stale entries.

### Related Patterns
Pairs with **4.2.1 Progressive Compression** for ageing entries.

### Anti‑Patterns
Global, unpartitioned board; no GC.

### When to Use
Open‑ended, multi‑step problem solving with many contributors.

---

## 2.2.2  Publish‑Subscribe Pattern
Tags : mature · medium‑complexity · decoupled

**Summary**  
Producers emit events to topics; subscribers react independently.

### Problem
Tight coupling blocks independent evolution.

### Forces
Fan‑out ↔ cost; ordering ↔ scalability; durability ↔ latency.

### Solution
```
Producer ──publish──▶ Topic ──deliver──▶ Sub1/Sub2/…
```
Core ops: Publish · Subscribe · Replay.

### Implementation Notes
Topic taxonomy; consumer groups; back‑pressure policies; retention.

### Variations
At‑most‑once fire‑and‑forget; exactly‑once with compaction.

### Benefits & Trade‑offs
+ Loose coupling; horizontal scale.  
− Ordering complexity; lag management.

### Example
Research events fan out to Summariser, Indexer, and Auditor.

### Operational Checklist
Monitor consumer lag; enforce schema registry; manage topic count.

### Related Patterns
Transport via **1.2**; sourcing via **8.7**.

### Anti‑Patterns
One topic for everything; schema‑less payloads.

### When to Use
Event‑centric systems; multi‑consumer fan‑out.

---

## 2.2.3  Stigmergic Communication Pattern
Tags : experimental · high‑complexity · indirect

**Summary**  
Agents coordinate by writing traces to an environment that influences others.

### Problem
Direct messaging cannot always capture distributed hints or cues.

### Forces
Signal strength ↔ noise; permanence ↔ adaptability; locality ↔ global view.

### Solution
```
Agent ──leave marker──▶ Environment ◀──sense/act── Agent
              decay/TTL
```
Core ops: Mark · Sense · Decay.

### Implementation Notes
Design marker types; decay functions; conflict avoidance; audit markers for safety.

### Variations
Digital pheromones; weighted maps; constraint fields.

### Benefits & Trade‑offs
+ Simple local rules can yield global coordination.  
− Hard to predict and debug emergent effects.

### Example
Route‑planning agents reinforce efficient paths; decay prunes poor ones.

### Operational Checklist
Watch for runaway reinforcement; cap marker density.

### Related Patterns
Complement to **2.2.1 Blackboard**.

### Anti‑Patterns
Unlimited persistence; no decay.

### When to Use
Swarm‑like behaviours; exploration/exploitation tasks.

---

## 2.3.1  Model Context Protocol (MCP)
Tags : emerging · medium‑complexity · standardised

**Summary**  
Connect agents/LLMs to tools and data sources with policy‑controlled calls.

### Problem
Tool access without discipline leads to leakage, loops, or runaway costs.

### Forces
Power ↔ safety; flexibility ↔ governance; latency ↔ completeness.

### Solution
```
Agent ──invoke(tool, scope)──▶ MCP Runtime ──call──▶ Tool/Data
           quotas + redaction         ◀─result──
```
Core ops: Tool list · Invoke · Quotas · Redaction.

### Implementation Notes
Permission scopes; input/output schemas; timeouts; cost budgets; observability.

### Variations
Local tool sandboxes; remote provider bridges.

### Benefits & Trade‑offs
+ Rich capability access; controlled surface.  
− Additional policy/ops work; latency.

### Example
Agent pulls docs via MCP search tool with redaction rules applied.

### Operational Checklist
Audit tool calls; cap budget; rotate credentials.

### Related Patterns
Pairs with **5.4 Tool Use**; leverages **8.3 Zero‑Trust**.

### Anti‑Patterns
Unscoped tool access; blind chaining.

### When to Use
Any tool‑calling agent in regulated or cost‑sensitive contexts.

---

## 2.3.2  Event‑Driven Architecture Pattern
Tags : mature · high‑complexity · scalable

**Summary**  
System reacts to events with asynchronous handlers and state transitions.

### Problem
Synchronous workflows hit scale and resilience limits.

### Forces
Ordering ↔ partitioning; consistency ↔ availability; replayability ↔ storage cost.

### Solution
```
Event Store ──stream──▶ Handlers ──emit──▶ New Events
         replay/compaction
```
Core ops: Emit · Handle · Replay.

### Implementation Notes
Idempotent handlers; schema evolution; dead‑letter; compaction.

### Variations
CQRS; saga orchestration; outbox.

### Benefits & Trade‑offs
+ Scale; resilience; auditability.  
− Complexity in design, ops, and troubleshooting.

### Example
Payment event triggers fulfilment and notifications independently.

### Operational Checklist
Track handler lag; test replays; manage schema evolution.

### Related Patterns
Leans on **8.7 Event Sourcing**; delivered via **1.2**.

### Anti‑Patterns
Stateful handlers without idempotence; tight coupling to event order.

### When to Use
High‑scale, loosely coupled domains.

---

# 3  Orchestration Patterns

## 3.1  Sequential Orchestration Pattern
Tags : mature · low‑complexity · deterministic

**Summary**  
Execute tasks in strict order with explicit dependencies.

### Problem
Parallelism complicates correctness when outputs depend on previous steps.

### Forces
Simplicity ↔ throughput; determinism ↔ flexibility.

### Solution
```
Step1 ─▶ Step2 ─▶ Step3
checkpoints + compensation
```
Core ops: Plan · Execute · Checkpoint.

### Implementation Notes
Compensation actions; idempotent steps; time budgets.

### Variations
Branching sequences; guarded steps.

### Benefits & Trade‑offs
+ Predictable behaviour.  
− Slower wall‑clock time.

### Example
Data ingest → clean → index → publish.

### Operational Checklist
Track step durations; alert on retries; persist checkpoints.

### Related Patterns
Pairs with **5.2 Planning**.

### Anti‑Patterns
Ad‑hoc sequencing; hidden dependencies.

### When to Use
Linear pipelines with strict ordering.

---

## 3.2  Concurrent Orchestration Pattern
Tags : mature · medium‑complexity · parallel

**Summary**  
Run independent tasks in parallel to reduce total time.

### Problem
Sequential flows waste waiting time for independent subtasks.

### Forces
Speed ↔ resource contention; parallelism ↔ coordination cost.

### Solution
```
Fan‑out ─▶ Task A
        ├▶ Task B
        └▶ Task C ──▶ Join
```
Core ops: Fan‑out · Join · Partial‑fail policy.

### Implementation Notes
Concurrency limits; shared‑state protection; join timeouts.

### Variations
Speculative execution; hedged requests.

### Benefits & Trade‑offs
+ Faster wall‑clock.  
− Complexity; possible duplicated work.

### Example
Fetch from 3 sources, then merge best answers.

### Operational Checklist
Monitor queue depth and thread pools; cap concurrency.

### Related Patterns
Feeds **5.1 Decomposition**.

### Anti‑Patterns
Unbounded parallelism.

### When to Use
Independent or weakly coupled subtasks.

---

## 3.3  Hierarchical Pattern
Tags : mature · medium‑complexity · structured

**Summary**  
Manager delegates tasks to workers and aggregates results.

### Problem
Flat groups struggle with coordination and load‑balancing.

### Forces
Control ↔ flexibility; fairness ↔ throughput.

### Solution
```
Manager ──assign──▶ Workers (leases/heartbeats)
Manager ◀─results/partials── Workers
```
Core ops: Assign · Lease · Aggregate · Reassign.

### Implementation Notes
Leases; heartbeats; pre‑emption; prioritisation.

### Variations
Multi‑level hierarchies; shard‑aware managers.

### Benefits & Trade‑offs
+ Clear ownership and scaling.  
− Manager bottlenecks if not sharded.

### Example
Manager splits research topics across workers, then composes report.

### Operational Checklist
Track lease expiries; worker saturation; queue age.

### Related Patterns
Leverages **1.3 Lifecycle**.

### Anti‑Patterns
Single manager with no failover.

### When to Use
Large task pools; heterogeneous expertise.

---

## 3.4  Group Chat Pattern
Tags : emerging · medium‑complexity · collaborative

**Summary**  
Agents collaborate via moderated conversational turns.

### Problem
Unstructured chat can drift, loop, or explode in length.

### Forces
Collaboration ↔ focus; openness ↔ guardrails; quality ↔ cost.

### Solution
```
Moderator ──turns/rubric──▶ Agents
Context gates + summarise‑between‑turns
```
Core ops: Turn‑taking · Summarise · Stop condition.

### Implementation Notes
Role prompts; summarisation gates; max‑turns; rubric scoring.

### Variations
Human in the room; weighted voting.

### Benefits & Trade‑offs
+ Diverse inputs; better creativity.  
− Risk of drift; higher cost.

### Example
Designer, Engineer, PM agents debate options; moderator picks a plan.

### Operational Checklist
Track token spend; enforce stop rules; archive summaries.

### Related Patterns
Ties to **7.1 Human‑in‑the‑Loop** and **5.3 Reflection**.

### Anti‑Patterns
Unlimited turns; no moderator.

### When to Use
Open‑ended design discussions; brainstorming.

---

## 3.5  Handoff Pattern
Tags : emerging · medium‑complexity · dynamic

**Summary**  
Switch active agent by capability/context during a task.

### Problem
Single agent cannot cover all skills efficiently.

### Forces
Specialisation ↔ coordination; speed ↔ completeness.

### Solution
```
Agent A ──handoff(context capsule)──▶ Agent B
```
Core ops: Select · Package context · Transfer · Confirm.

### Implementation Notes
Capability router; context capsule schema; audit log.

### Variations
Round‑robin within a skill pool; confidence‑based routing.

### Benefits & Trade‑offs
+ Best‑fit expertise; clearer boundaries.  
− Additional complexity; potential context loss.

### Example
Research → Translation → Report with audited handoffs.

### Operational Checklist
Record handoffs; measure success rate; verify context completeness.

### Related Patterns
Needs **1.1 Registry** and **5.5 Capability Discovery**.

### Anti‑Patterns
Implicit handoffs with no audit.

### When to Use
Multi‑skill flows; compliance constraints.

---

## 3.6  Market‑Based Coordination Pattern
Tags : experimental · high‑complexity · distributed

**Summary**  
Allocate tasks via bids based on utility/cost.

### Problem
Central schedulers struggle with heterogeneous agents and dynamic costs.

### Forces
Efficiency ↔ fairness; transparency ↔ gaming; speed ↔ optimality.

### Solution
```
Auctioneer ──announce──▶ Bidders
Auctioneer ◀──bids/claims─ Bidders ──▶ Award
```
Core ops: Announce · Bid · Award · Settle.

### Implementation Notes
Bid strategies; reserve prices; anti‑collusion rules; audits.

### Variations
First‑price; Vickrey; continuous double auction.

### Benefits & Trade‑offs
+ Adaptive allocation.  
− Complexity; attack surface for gaming.

### Example
Compute‑heavy tasks auctioned to agents with spare GPU budget.

### Operational Checklist
Monitor bid distribution; detect collusion; cap volatility.

### Related Patterns
Combine with **8.4 Version Negotiation** for evolving rules.

### Anti‑Patterns
Opaque rules; unlimited bid changes.

### When to Use
Heterogeneous costs/capabilities; elastic supply.

---

# 4  Context Management Patterns

## 4.1.1  Shared Memory Pattern
Tags : mature · medium‑complexity · fundamental

**Summary**  
Central store for shared context with controlled access.

### Problem
Agents duplicate state or drift when state lives only locally.

### Forces
Accessibility ↔ privacy; freshness ↔ cost; structure ↔ flexibility.

### Solution
```
Agents ◀──get/put── Shared Memory ──audit──▶ Observability
```
Core ops: Put · Get · List · Audit.

### Implementation Notes
Schemas; TTLs; access control; provenance; encryption at rest.

### Variations
Namespace partitioning; per‑tenant stores.

### Benefits & Trade‑offs
+ Single source of truth; reuse.  
− Cost; contention; governance load.

### Example
Agents share current project state via a structured document.

### Operational Checklist
Monitor size, hot keys, and access patterns; expire old entries.

### Related Patterns
Feeds **4.2.1 Progressive Compression**.

### Anti‑Patterns
Blob dumping without schema; no TTLs.

### When to Use
Any multi‑agent context beyond trivial size.

---

## 4.1.2  Semantic Memory Pattern
Tags : emerging · medium‑complexity · knowledge

**Summary**  
Store facts/concepts for semantic retrieval (embeddings or triples).

### Problem
Keyword search misses relevant knowledge; duplication proliferates.

### Forces
Precision ↔ recall; freshness ↔ compute; ontology rigidity ↔ agility.

### Solution
```
Docs ──index/ETL──▶ Semantic Store ◀──semantic query── Agents
```
Core ops: Index · Link · Query.

### Implementation Notes
Ontology governance; deduplication; provenance; periodic re‑indexing.

### Variations
Vector store; RDF/knowledge graph; hybrid.

### Benefits & Trade‑offs
+ Better recall/precision.  
− Drift management; maintenance.

### Example
Agent searches “cold boot GPU” and retrieves related concepts, not only exact phrases.

### Operational Checklist
Track hit‑rates; drift; stale embeddings.

### Related Patterns
Works with **6.2.1 Shared Knowledge Store**.

### Anti‑Patterns
Uncontrolled taxonomies; opaque embeddings.

### When to Use
Cross‑domain knowledge needs and ambiguous queries.

---

## 4.1.3  Episodic Memory Pattern
Tags : emerging · medium‑complexity · experience

**Summary**  
Record interactions/events with timestamps and participants.

### Problem
Without episodes, agents lose history needed for continuity and learning.

### Forces
Retention ↔ privacy; detail ↔ cost; speed ↔ completeness.

### Solution
```
Agent ──append(event)──▶ Episode Log ──summarise/replay──▶ Agent
```
Core ops: Append · Summarise · Replay.

### Implementation Notes
PII handling; retention policies; summarisation cadence.

### Variations
Session‑scoped logs; per‑user episodes.

### Benefits & Trade‑offs
+ Continuity and learning.  
− Storage and privacy management.

### Example
Support agent recalls prior resolutions before answering.

### Operational Checklist
Monitor growth; summarisation quality; access control violations.

### Related Patterns
Feeds **4.2.3 Insight Distillation** and **9.3 Experience Replay**.

### Anti‑Patterns
Infinite retention; raw logs without summarisation.

### When to Use
Conversational or longitudinal workflows.

---

## 4.1.4  Procedural Memory Pattern
Tags : emerging · high‑complexity · skills

**Summary**  
Capture learned procedures/skills for reuse.

### Problem
Tacit skill remains trapped in prompts or ad‑hoc scripts.

### Forces
Standardisation ↔ creativity; safety ↔ speed; versioning ↔ simplicity.

### Solution
```
Skill Spec ◀──promote/test── Training/Derivation ◀──examples
```
Core ops: Derive · Test · Promote · Version.

### Implementation Notes
Approval gates; safety tests; rollback; deprecation.

### Variations
Prompt‑libraries; small adapters; distilled mini‑models.

### Benefits & Trade‑offs
+ Faster, consistent execution.  
− Governance burden; risk of fossilisation.

### Example
Successful “red‑team review” process promoted into a reusable skill.

### Operational Checklist
Track adoption; failure rates; drift; retire outdated skills.

### Related Patterns
Links to **9.5 Continuous Fine‑Tuning** for weight‑level changes.

### Anti‑Patterns
Shadow skills; no testing.

### When to Use
Recurring tasks where proven procedures exist.

---

## 4.2.1  Progressive Compression Pattern
Tags : mature · medium‑complexity · scalability

**Summary**  
Summarise ageing context recursively to retain signal under size limits.

### Problem
Context windows and stores cannot grow without bounds.

### Forces
Detail ↔ footprint; recall ↔ cost; speed ↔ fidelity.

### Solution
```
Raw → Summary → Summary‑of‑summaries
```
Core ops: Summarise · Validate · Evict originals per policy.

### Implementation Notes
Quality checks; reversible archives; thresholds per agent.

### Variations
Semantic vs extractive; tiered storage.

### Benefits & Trade‑offs
+ Predictable memory footprint.  
− Possible loss of nuance.

### Example
Daily roll‑ups of research chat to weekly/monthly capsules.

### Operational Checklist
Measure retrieval quality pre/post compression.

### Related Patterns
Pairs with **4.2.2 Selective Pruning**.

### Anti‑Patterns
Blind compression without QA; no provenance.

### When to Use
Any long‑running context stream.

---

## 4.2.2  Selective Pruning Pattern
Tags : mature · medium‑complexity · efficiency

**Summary**  
Remove irrelevant context via scores/policies while keeping essentials.

### Problem
Irrelevant data increases latency and cost.

### Forces
Aggressiveness ↔ recall; automation ↔ safety; explainability ↔ complexity.

### Solution
```
Context ──score/filter──▶ Keep | Archive | Drop
```
Core ops: Score · Filter · Explain.

### Implementation Notes
Feature scores; human‑approved rules for sensitive data; reversible archive for critical classes.

### Variations
Static rules; learned relevance models.

### Benefits & Trade‑offs
+ Lower cost; faster retrieval.  
− Risk of removing useful items.

### Example
Keep “decisions”, archive “raw logs”, drop “duplicates”.

### Operational Checklist
Review false‑drop rates; allow overrides.

### Related Patterns
Follows **4.2.1 Progressive Compression**.

### Anti‑Patterns
No explainability; irreversible deletion.

### When to Use
Bounded budgets or latency targets.

---

## 4.2.3  Insight Distillation Pattern
Tags : emerging · high‑complexity · intelligence

**Summary**  
Extract key decisions and rationales from raw interactions for reuse.

### Problem
Logs contain insight but little structure.

### Forces
Faithfulness ↔ brevity; automation ↔ accuracy; bias control ↔ speed.

### Solution
```
Logs ──distil→ Insights (decisions, rationales, metrics)
```
Core ops: Extract · Validate · Store.

### Implementation Notes
Schemas for insights; confidence scores; human review for critical paths.

### Variations
LLM‑assisted extraction; rule‑based extraction; hybrids.

### Benefits & Trade‑offs
+ Faster onboarding; better reuse.  
− Risk of mis‑extraction; review load.

### Example
Agent distils “approval rules” from past tasks; future tasks reuse them.

### Operational Checklist
Spot‑check faithfulness; track usage.

### Related Patterns
Feeds **9.1 Reflection Loop** and **9.3 Experience Replay**.

### Anti‑Patterns
Free‑text summaries without structure.

### When to Use
Mature systems with substantial logs.

---

# 5  Task Management Patterns

## 5.1  Task Decomposition Pattern
Tags : mature · medium‑complexity · planning

**Summary**  
Split complex goals into manageable subtasks.

### Problem
Monolithic tasks hide dependencies and stall progress.

### Forces
Granularity ↔ overhead; depth ↔ explosion; autonomy ↔ coordination.

### Solution
```
Goal ──plan──▶ Subtasks (ordered graph)
```
Core ops: Plan · Order · Bound depth.

### Implementation Notes
Dependency graphs; stop criteria; ownership per node.

### Variations
Recursive decomposition; templated task graphs.

### Benefits & Trade‑offs
+ Clarity; parallelism.  
− Planning overhead.

### Example
Research → outline → draft → review → publish.

### Operational Checklist
Track plan accuracy vs execution; prune unused branches.

### Related Patterns
Works with **3.2 Concurrent Orchestration**.

### Anti‑Patterns
Unbounded recursion.

### When to Use
Complex goals with obvious sub‑steps.

---

## 5.2  Planning Pattern
Tags : mature · medium‑complexity · strategic

**Summary**  
Form a plan before acting; revise as evidence arrives.

### Problem
Act‑first approaches waste tokens/time and reduce predictability.

### Forces
Upfront cost ↔ fewer retries; rigidity ↔ adaptivity.

### Solution
```
Plan → Execute → Reflect → Update Plan
```
Core ops: Draft plan · Execute · Reflect · Update.

### Implementation Notes
Plan budget; stop rules; capture assumptions.

### Variations
Model‑generated plans; human‑approved plans.

### Benefits & Trade‑offs
+ Fewer dead‑ends; clearer audits.  
− Slight upfront cost.

### Example
Plan top‑k sources to query before hitting APIs.

### Operational Checklist
Log plan deltas; compare predicted vs actual effort.

### Related Patterns
Feeds **5.3 Reflection**, **3.1 Sequential**.

### Anti‑Patterns
Hidden plans; plan‑drift without update.

### When to Use
Expensive or high‑risk tasks.

---

## 5.3  Reflection Pattern
Tags : mature · medium‑complexity · improvement

**Summary**  
Self‑critique outputs and adjust approach for the next attempt.

### Problem
Repeating the same mistake burns budget and trust.

### Forces
Thoroughness ↔ speed; automation ↔ reliability.

### Solution
```
Draft → Score with rubric → Revise or Stop
```
Core ops: Critique · Score · Revise.

### Implementation Notes
Explicit rubrics; cap retries; log learnings into memory.

### Variations
Self‑reflection; peer‑reflection; human‑assisted review.

### Benefits & Trade‑offs
+ Continuous improvement.  
− Extra cycles if misused.

### Example
Use a checklist for correctness and tone before sending output.

### Operational Checklist
Track improvement deltas; flag loops.

### Related Patterns
Drives **9.1 Reflection Loop** (behavioural scale).

### Anti‑Patterns
Vague “try again”; no rubric.

### When to Use
Any iterative generation or decision task.

---

## 5.4  Tool Use Pattern
Tags : mature · low‑complexity · integration

**Summary**  
Invoke external tools/APIs under policy to extend capabilities.

### Problem
Re‑implementing tools inside agents leads to duplication and risk.

### Forces
Power ↔ safety; latency ↔ completeness.

### Solution
```
Agent ──invoke(tool)──▶ Tool
      ◀──validate/timeout
```
Core ops: Discover tool; Validate; Invoke; Handle failure.

### Implementation Notes
Schema validation; timeouts; rate‑limits; sandbox side‑effects; logging.

### Variations
Local tools; remote SaaS; MCP‑mediated.

### Benefits & Trade‑offs
+ Leverages existing systems.  
− Integration and ops complexity.

### Example
Call spreadsheet tool to compute totals rather than prompting LLM math.

### Operational Checklist
Audit tool errors; cap retries; rotate secrets.

### Related Patterns
See **2.3.1 MCP**, **8.3 Zero‑Trust**.

### Anti‑Patterns
Unvalidated inputs; unbounded retries.

### When to Use
Any external computation or data fetch.

---

## 5.5  Capability Discovery Pattern
Tags : emerging · medium‑complexity · dynamic

**Summary**  
Discover and advertise agent capabilities dynamically beyond name/address.

### Problem
Name‑based lookup misses best‑fit skills.

### Forces
Expressiveness ↔ complexity; freshness ↔ overhead.

### Solution
```
Agent ──advertise(skill, constraints)──▶ Registry
Requester ──query(by skill)─────────────▶ Registry
```
Core ops: Advertise · Query · Rank · Expire.

### Implementation Notes
Capability schema/ontology; ranking; TTL/expiry; trust signals.

### Variations
Semantic similarity search; certification badges.

### Benefits & Trade‑offs
+ Better routing; modular growth.  
− Ontology maintenance; spam risk.

### Example
Router picks “vision‑ocr v2” over generic “reader”.

### Operational Checklist
Review false‑match rate; prune stale ads.

### Related Patterns
Builds on **1.1 Registry**; feeds **3.5 Handoff**.

### Anti‑Patterns
Free‑text ads; no expiry.

### When to Use
Evolving ecosystems with many skills.

---

# 6  Knowledge Management Patterns

## 6.1  Two‑Stage Knowledge Pipeline Pattern
Tags : emerging · high‑complexity · comprehensive

**Summary**  
Manage granular findings and synthesised knowledge via two coordinated paths.

### Problem
Raw notes pile up; published knowledge lags reality.

### Forces
Speed ↔ rigour; granularity ↔ readability; provenance ↔ concision.

### Solution
```
Findings → curation/QA → Knowledge Articles
           (parallel: raw store for reuse)
```
Core ops: Capture · Curate · Publish.

### Implementation Notes
Source tracking; QA gates; promotion rules; feedback loop.

### Variations
Editorial board; automated summarisation + human QA.

### Benefits & Trade‑offs
+ Fewer duplicate efforts; trustworthy outputs.  
− Workflow overhead.

### Example
Research outputs flow into a curated knowledge base and a raw store for RAG.

### Operational Checklist
Track duplicate‑rate; time‑to‑publish; citation integrity.

### Related Patterns
Works with **6.2.1 Shared Knowledge Store** and **4.2.3 Insight Distillation**.

### Anti‑Patterns
One bucket for everything; no curation.

### When to Use
Teams that research continuously.

---

## 6.2  Knowledge‑Storage Patterns

### 6.2.1  Shared Knowledge Store Pattern
Tags : emerging · medium‑complexity · reuse

**Summary**  
Common repository supports fuzzy retrieval and structured access.

### Problem
Teams repeat research due to inaccessible prior work.

### Forces
Recall ↔ precision; cost ↔ freshness; structure ↔ agility.

### Solution
```
Agents ──put/get/search──▶ Vector/Graph/Hybrid Store
```
Core ops: Upsert · Search · Rank · Attribute.

### Implementation Notes
Chunking; metadata; provenance; re‑index schedules.

### Variations
Vector‑augmented; graph‑augmented; hybrid router.

### Benefits & Trade‑offs
+ Reuse; faster delivery.  
− Maintenance and drift.

### Example
Agent searches embeddings then traverses a graph for relationships.

### Operational Checklist
Measure hit‑rates; stale index detection; cost budgets.

### Related Patterns
Pairs with **4.1.2 Semantic Memory**.

### Anti‑Patterns
Dumping PDFs without metadata; stale indices.

### When to Use
Any shared research/knowledge environment.

---

# 7  Human Integration Patterns

## 7.1  Human‑in‑the‑Loop Pattern
Tags : mature · medium‑complexity · oversight

**Summary**  
Humans approve, correct, or guide at key points.

### Problem
Fully autonomous loops can drift or violate constraints.

### Forces
Quality ↔ speed; autonomy ↔ trust; load ↔ coverage.

### Solution
```
Agent ──propose + evidence──▶ Human ──approve/correct──▶ Agent
```
Core ops: Propose · Review · Decide.

### Implementation Notes
Clear UI; latency budgets; audit trail; escalation paths.

### Variations
Sampling reviews; risk‑tiered gates.

### Benefits & Trade‑offs
+ Trust and safety.  
− Added latency and cost.

### Example
Human approves contract terms before sending.

### Operational Checklist
Track approval latency; error‑catch rate; reviewer load.

### Related Patterns
Integrates with **3.4 Group Chat** and **5.3 Reflection**.

### Anti‑Patterns
Opaque decisions; no evidence surfaced.

### When to Use
High‑risk outputs; regulated environments.

---

## 7.2  User Elicitation Pattern
Tags : emerging · medium‑complexity · clarification

**Summary**  
System asks targeted questions to reduce ambiguity.

### Problem
Vague inputs cause rework and poor outputs.

### Forces
Speed ↔ clarity; intrusiveness ↔ engagement.

### Solution
```
Agent ──ask minimal, high‑value questions──▶ User
```
Core ops: Detect ambiguity · Ask · Confirm.

### Implementation Notes
Question design; stop rules; store assumptions.

### Variations
Wizard‑of‑Oz; progressive disclosure.

### Benefits & Trade‑offs
+ Better results, fewer retries.  
− User fatigue if overused.

### Example
Clarify acceptance criteria and deadline before starting.

### Operational Checklist
Track question count; measure reduction in rework.

### Related Patterns
Pairs with **5.2 Planning**.

### Anti‑Patterns
Laundry‑list questioning; repeating questions.

### When to Use
Ambiguous inputs and costly retries.

---

## 7.3  Explainability Pattern
Tags : emerging · high‑complexity · transparency

**Summary**  
Expose reasons, inputs, and limits of decisions.

### Problem
Opaque agents undermine trust and debugging.

### Forces
Detail ↔ readability; privacy ↔ accountability.

### Solution
```
Decision → Evidence links + Rationale + Limits
```
Core ops: Capture rationale · Link evidence · Present clearly.

### Implementation Notes
Citations; model‑agnostic summaries; privacy controls.

### Variations
Counterfactuals; saliency maps.

### Benefits & Trade‑offs
+ Trust; faster incident response.  
− Extra work; possible information leaks.

### Example
Report shows sources, decision checklist, and constraints.

### Operational Checklist
QA rationales; redact sensitive data; check broken links.

### Related Patterns
Leverages **8.7 Event Sourcing** for audit.

### Anti‑Patterns
Hand‑wavy statements; missing evidence.

### When to Use
Decision support and regulated outputs.

---

## 7.4  Trust‑Building Pattern
Tags : emerging · medium‑complexity · adoption

**Summary**  
Increase autonomy gradually with transparency and predictable behaviour.

### Problem
Jumping to full autonomy spooks users and leadership.

### Forces
Speed ↔ acceptance; experimentation ↔ safety.

### Solution
```
Alpha (observer) → Beta (suggest) → GA (act) with rollback
```
Core ops: Stage gates · Confidence scoring · Rollback.

### Implementation Notes
Progressive rollout; dashboards; incident response plan.

### Variations
Per‑capability graduation; user‑opt‑in pilots.

### Benefits & Trade‑offs
+ Smoother adoption.  
− Longer path to full autonomy.

### Example
Agent starts as “copilot” before moving to auto‑execute for low‑risk tasks.

### Operational Checklist
Track incident rate; user satisfaction; autonomy coverage.

### Related Patterns
Works with **9.1 Reflection Loop**.

### Anti‑Patterns
Big‑bang launches; opaque changes.

### When to Use
Any new autonomous capability.

---

# 8  System‑Quality Patterns

## 8.1.1  Resilient Communication Pattern
Tags : mature · high‑complexity · reliability

**Summary**  
Communication layer tolerates faults via retries, timeouts, and failover.

### Problem
Networks and components fail in unpredictable ways.

### Forces
Reliability ↔ latency; cost ↔ redundancy.

### Solution
```
Client ──▶ Primary ──failover──▶ Secondary
  timeouts + circuit‑breakers
```
Core ops: Retry · Backoff · Failover.

### Implementation Notes
Idempotence; hedged requests; multi‑AZ; chaos testing.

### Variations
Geo‑replication; quorum writes.

### Benefits & Trade‑offs
+ Higher availability.  
− Extra cost and complexity.

### Example
Hedge slow reads after 95th percentile threshold.

### Operational Checklist
SLOs; error budgets; synthetic probes.

### Related Patterns
Relies on **1.2 Transport**.

### Anti‑Patterns
Retry storms; no jitter/backoff.

### When to Use
Any critical path.

---

## 8.2  Observability Pattern
Tags : emerging · medium‑complexity · diagnostics

**Summary**  
Tracing, metrics, and logs deliver runtime insight.

### Problem
Without visibility, incident response and optimisation drag on.

### Forces
Detail ↔ cost; sampling ↔ accuracy.

### Solution
```
Trace (correlation‑ID) + Metrics (RED/USE) + Logs (structured)
```
Core ops: Instrument · Collect · Visualise.

### Implementation Notes
Correlation across agents; exemplars; dashboards; SLOs.

### Variations
Adaptive sampling; trace‑based testing.

### Benefits & Trade‑offs
+ Faster diagnosis; performance tuning.  
− Storage and processing overhead.

### Example
Per‑request traces reveal bottleneck in translation agent.

### Operational Checklist
Budget storage; prune noisy logs; test alerts.

### Related Patterns
Uses **8.6 Standardised Message Format** for IDs.

### Anti‑Patterns
Print‑debug in production; no SLOs.

### When to Use
Always—start day one.

---

## 8.3.1  Identity Propagation Pattern
Tags : emerging · medium‑complexity · security

**Summary**  
Carry caller identity/scope across agent hops.

### Problem
Lost identity breaks auditing and least‑privilege enforcement.

### Forces
Security ↔ usability; performance ↔ cryptographic cost.

### Solution
```
JWT/mTLS identity → propagated via envelopes/headers
```
Core ops: Issue · Validate · Propagate.

### Implementation Notes
Short‑lived tokens; rotation; audience checks; replay protection.

### Variations
SPIFFE/SPIRE; OAuth service‑to‑service.

### Benefits & Trade‑offs
+ Traceable actions; scoped access.  
− Token management overhead.

### Example
Downstream agent checks scope “translate:fr” before acting.

### Operational Checklist
Alert on invalid tokens; clock‑skew handling.

### Related Patterns
Pairs with **8.3.3 Zero‑Trust Boundary**.

### Anti‑Patterns
Shared secrets; long‑lived tokens.

### When to Use
Any multi‑hop call chain.

---

## 8.3.2  Encrypted Message Bus Pattern
Tags : emerging · medium‑complexity · security

**Summary**  
Encrypt data in transit across transport and topics.

### Problem
Unencrypted channels expose sensitive data.

### Forces
Security ↔ latency; key rotation ↔ availability.

### Solution
```
Producer/Consumer ↔ TLS‑protected Broker; signed envelopes
```
Core ops: Encrypt · Verify · Rotate keys.

### Implementation Notes
TLS everywhere; strict ciphers; cert rotation; envelope signatures.

### Variations
Client‑side encryption; double encryption for sensitive topics.

### Benefits & Trade‑offs
+ Confidentiality and integrity.  
− Operational burden.

### Example
Sensitive events flow only over TLS with signed payloads.

### Operational Checklist
Enforce TLS policy; test expiry; monitor renegotiations.

### Related Patterns
Works with **1.2 Transport**, **8.6 Message Format**.

### Anti‑Patterns
Downgrade to plaintext; unmanaged keys.

### When to Use
Always for non‑public data.

---

## 8.3.3  Zero‑Trust Boundary Pattern
Tags : emerging · high‑complexity · security

**Summary**  
Authenticate and authorise every call; assume hostile network.

### Problem
Implicit trust enables lateral movement and privilege creep.

### Forces
Security ↔ complexity; performance ↔ verification.

### Solution
```
Policy Engine + Mutual Auth + Deny‑by‑Default
```
Core ops: Authenticate · Authorise · Audit.

### Implementation Notes
OPA/ABAC; sidecars; policy CI; least‑privilege defaults.

### Variations
Micro‑segmentation; per‑capability boundaries.

### Benefits & Trade‑offs
+ Strong security posture.  
− Policy management overhead.

### Example
Agent fails without proper scope despite being inside the cluster.

### Operational Checklist
Policy drift tests; regular reviews; incident runbooks.

### Related Patterns
Requires **8.3.1 Identity Propagation**.

### Anti‑Patterns
Flat networks; blanket allow‑lists.

### When to Use
Any environment with sensitive data or external exposure.

---

## 8.4  Version Negotiation Pattern
Tags : emerging · medium‑complexity · interoperability

**Summary**  
Coexist old and new message formats and features; upgrade gracefully.

### Problem
Lock‑step upgrades cause outages and slow delivery.

### Forces
Stability ↔ evolution; compatibility ↔ simplicity.

### Solution
```
Hello → versions/features → agree → run
```
Core ops: Advertise · Negotiate · Deprecate.

### Implementation Notes
Schema registry; feature flags; compatibility tests; timelines.

### Variations
Per‑feature negotiation; per‑topic versions.

### Benefits & Trade‑offs
+ Safer upgrades.  
− More states to test.

### Example
New summariser runs v3 while others stay on v2 until sunset.

### Operational Checklist
Monitor version split; publish deprecation notices.

### Related Patterns
Integrates with **2.1.2 A2A** and **8.6 Message Format**.

### Anti‑Patterns
Silent breaking changes.

### When to Use
Multi‑team, rolling upgrade environments.

---

## 8.5  Configuration‑Driven Capabilities Pattern
Tags : emerging · medium‑complexity · flexibility

**Summary**  
Enable/disable capabilities via configuration without redeploys.

### Problem
Code pushes for small toggles slow iteration and increase risk.

### Forces
Flexibility ↔ safety; speed ↔ validation.

### Solution
```
Config Store ⇄ Agents (hot‑reload with validation)
```
Core ops: Validate · Apply · Rollback.

### Implementation Notes
Schema validation; audit trail; safe defaults; staged rollout.

### Variations
Per‑tenant flags; percentage rollouts.

### Benefits & Trade‑offs
+ Faster iteration; fewer deployments.  
− Misconfiguration risk.

### Example
Enable “market‑based allocation” for 10% of traffic first.

### Operational Checklist
Config linting in CI; change‑watch alerts.

### Related Patterns
Pairs with **8.2 Observability** for safe rollout.

### Anti‑Patterns
Runtime eval of unvalidated configs.

### When to Use
Feature rollout and rapid experimentation.

---

## 8.6  Standardised Message Format Pattern
Tags : mature · low‑complexity · interoperability

**Summary**  
Consistent envelopes enable interop and tooling.

### Problem
Inconsistent payloads block routing and observability.

### Forces
Minimalism ↔ extensibility; strictness ↔ agility.

### Solution
```
Envelope: type, version, ids, timestamps, auth, payload, signature
```
Core ops: Validate · Parse · Extend via headers.

### Implementation Notes
Schema registry; required vs optional fields; backwards compatibility.

### Variations
Binary vs JSON; header plugins.

### Benefits & Trade‑offs
+ Tooling and interop.  
− Upfront schema work.

### Example
Shared envelope lets tracing tie events end‑to‑end.

### Operational Checklist
Lint in CI; reject unknown types.

### Related Patterns
Foundational for **2.1.2 A2A**, **1.2 Transport**.

### Anti‑Patterns
Free‑form JSON; no versions.

### When to Use
Immediately—do not delay standardisation.

---

## 8.7  Event Sourcing Pattern
Tags : mature · high‑complexity · auditability

**Summary**  
Persist events as the source of truth; rebuild state by replay.

### Problem
State snapshots alone lose history and complicate recovery.

### Forces
Auditability ↔ storage; simplicity ↔ power.

### Solution
```
Append‑only Log → Projectors → Materialised Views
```
Core ops: Append · Project · Replay.

### Implementation Notes
Idempotent projectors; compaction; GDPR/PII strategies; schema evolution.

### Variations
Outbox pattern; snapshotting.

### Benefits & Trade‑offs
+ Full history; recovery; temporal queries.  
− Operational complexity; storage cost.

### Example
Rebuild knowledge index after bug fix by replaying events.

### Operational Checklist
Test replay regularly; monitor projector lag; secure logs.

### Related Patterns
Supports **2.3.2 EDA**, **7.3 Explainability**.

### Anti‑Patterns
Mutable event logs; changing past events.

### When to Use
High‑audit domains; recovery needs; temporal analytics.

---

# 9  Self‑Improvement Patterns

## 9.1  Reflection Loop (see 5.3)
Tags : mature · medium‑complexity · behavioural

**Summary**  
Apply reflection continually to improve behaviour over time.

### Need‑to‑know
Rubrics; outcome memory; avoid overfitting; stop rules.

---

## 9.2  Social Learning Pattern
Tags : emerging · medium‑complexity

**Summary**  
Agents observe peer outcomes and adopt winning strategies.

### Key Points
Broadcast results with trust signals; prevent herd failures; log adoptions.

---

## 9.3  Experience Replay Pattern
Tags : emerging · medium‑complexity

**Summary**  
Sample past interactions to refine prompts or small models.

### Key Points
Curate examples; privacy hygiene; detect drift; periodic refresh.

---

## 9.4  Evolutionary Population Pattern
Tags : experimental · high‑complexity

**Summary**  
Maintain a population; evolve via selection and mutation.

### Key Points
Fitness metrics; diversity; kill‑switch; compute budgets.

---

## 9.5  Continuous Fine‑Tuning Pattern
Tags : mature · high‑complexity

**Summary**  
Apply small weight updates during service with guardrails.

### Key Points
Shadow evaluation; checkpoints; fast rollback; strict safety gates.

---

## 9.6  Reward‑Shaping Feedback Pattern
Tags : emerging · medium‑complexity

**Summary**  
Use human/heuristic rewards to steer behaviour.

### Key Points
Stable reward channel; anti‑gaming checks; rate limits.

---

## 9.7  Safety‑Guard Adaptation Pattern
Tags : experimental · medium‑complexity · safety

**Summary**  
Guards adjust thresholds/rules using violation logs.

### Key Points
Reviewer loop; caps on auto‑tightening; signed configs.

---

# 10  Anti‑Patterns (brief catalogue)

- **Context Explosion** — push too much context; summarise and fetch on demand.  
- **Tight Coupling** — depend on specific formats/addresses; use registry/contracts.  
- **Synchronous Blocking** — long waits; prefer async queues.  
- **Memory Leaks** — unbounded growth; retention, pruning, compression.  
- **Lost Updates** — concurrent stomps; locks/CRDTs/conflict alerts.  
- **Over‑Orchestration** — needless complexity; start simple.  
- **Tool Lock‑in** — deep framework ties; protocol‑first, adapters.  
- **Monolithic Agents** — do‑everything agents; split capabilities.

---

# 11  Tag Definitions

**Maturity** — mature · emerging · experimental  
**Complexity** — low · medium · high  
**Characteristics** — required · synchronous · standardised · scalable · collaborative · deterministic · dynamic · reliability · transparency · security · auditability · interoperability · flexibility

