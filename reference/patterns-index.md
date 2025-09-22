# 📚 Agentic Patterns Index

> Quick reference guide to all multi-agent system patterns, organized by category

## Navigation
- [Foundation Patterns](#foundation-patterns) (3)
- [Communication Patterns](#communication-patterns) (9)
- [Orchestration Patterns](#orchestration-patterns) (6)
- [Context Management Patterns](#context-management-patterns) (7)
- [Task Management Patterns](#task-management-patterns) (5)
- [Knowledge Management Patterns](#knowledge-management-patterns) (2)
- [Human Integration Patterns](#human-integration-patterns) (4)
- [System Quality Patterns](#system-quality-patterns) (10)
- [Self-Improvement Patterns](#self-improvement-patterns) (7)

---

## Foundation Patterns
*Required infrastructure components for multi-agent systems*

### [1.1 Agent Registry Pattern](./docs/patterns/foundation/agent-registry.md)
**Tags**: `mature` `medium-complexity` `required`
**Problem**: Hard-coded endpoints create fragility and block evolution
**Solution**: Catalogue where agents register identity/capabilities and discover peers at runtime
**When to Use**: > 3 agents, multi-team development, rolling evolution
**Related**: Requires Message Transport · Enables Capability Discovery

### [1.2 Message Transport Pattern](./docs/patterns/foundation/message-transport.md)
**Tags**: `mature` `low-complexity` `required`
**Problem**: Ad-hoc HTTP/sockets diverge in schema and retry logic
**Solution**: Shared queue/bus/stream with acknowledgements and retries
**When to Use**: ≥ 2 agents requiring async coordination
**Related**: Works with Publish-Subscribe · Required by Agent Registry

### [1.3 Agent Lifecycle Management Pattern](./docs/patterns/foundation/lifecycle-management.md)
**Tags**: `mature` `medium-complexity`
**Problem**: Without lifecycle hooks, restart storms and zombie agents accumulate
**Solution**: Standard hooks for create, start, pause, resume, scale, retire under supervision
**When to Use**: Multi-node deployments, bursty workloads, rolling updates
**Related**: Interacts with Resilient Communication · Depends on Registry

---

## Communication Patterns
*How agents exchange information and coordinate*

### [2.1.1 Request-Reply Pattern](./docs/patterns/communication/request-reply.md)
**Tags**: `mature` `low-complexity` `synchronous`
**Problem**: Blocking calls can stall pipelines and amplify failures
**Solution**: Simple synchronous query-response between agents
**When to Use**: Low-latency reads or control paths with bounded work
**Related**: Use Version Negotiation · Consider EDA for async

### [2.1.2 Agent-to-Agent (A2A) Protocol](./docs/patterns/communication/a2a-protocol.md)
**Tags**: `emerging` `medium-complexity` `standardised`
**Problem**: Heterogeneous agents struggle without common contract
**Solution**: Shared schema/handshake for direct interactions with capability negotiation
**When to Use**: Cross-team or cross-language agent meshes
**Related**: Leans on Standardised Message Format

### [2.2.1 Blackboard Pattern](./docs/patterns/communication/blackboard.md)
**Tags**: `mature` `medium-complexity` `collaborative`
**Problem**: Complex problems need incremental multi-specialist contributions
**Solution**: Shared workspace where agents post partial solutions
**When to Use**: Open-ended, multi-step problem solving
**Related**: Pairs with Progressive Compression

### [2.2.2 Publish-Subscribe Pattern](./docs/patterns/communication/publish-subscribe.md)
**Tags**: `mature` `medium-complexity` `decoupled`
**Problem**: Tight coupling blocks independent evolution
**Solution**: Producers emit events; subscribers react independently
**When to Use**: Event-centric systems, multi-consumer fan-out
**Related**: Transport via Message Transport · Sourcing via Event Sourcing

### [2.2.3 Stigmergic Communication Pattern](./docs/patterns/communication/stigmergic.md)
**Tags**: `experimental` `high-complexity` `indirect`
**Problem**: Direct messaging cannot capture distributed hints/cues
**Solution**: Agents coordinate by writing traces to environment
**When to Use**: Swarm-like behaviors, exploration/exploitation
**Related**: Complement to Blackboard

### [2.3.1 Model Context Protocol (MCP)](./docs/patterns/communication/mcp.md)
**Tags**: `emerging` `medium-complexity` `standardised`
**Problem**: Tool access without discipline leads to leakage/loops
**Solution**: Connect agents/LLMs to tools with policy-controlled calls
**When to Use**: Tool-calling agents in regulated/cost-sensitive contexts
**Related**: Pairs with Tool Use · Leverages Zero-Trust

### [2.3.2 Event-Driven Architecture Pattern](./docs/patterns/communication/eda.md)
**Tags**: `mature` `high-complexity` `scalable`
**Problem**: Synchronous workflows hit scale/resilience limits
**Solution**: System reacts to events with async handlers and state transitions
**When to Use**: High-scale, loosely coupled domains
**Related**: Leans on Event Sourcing · Delivered via Transport

---

## Orchestration Patterns
*Coordinating agent work and task distribution*

### [3.1 Sequential Orchestration Pattern](./docs/patterns/orchestration/sequential.md)
**Tags**: `mature` `low-complexity` `deterministic`
**Problem**: Parallelism complicates when outputs depend on previous steps
**Solution**: Execute tasks in strict order with explicit dependencies
**When to Use**: Linear pipelines with strict ordering
**Related**: Pairs with Planning Pattern

### [3.2 Concurrent Orchestration Pattern](./docs/patterns/orchestration/concurrent.md)
**Tags**: `mature` `medium-complexity` `parallel`
**Problem**: Sequential flows waste time on independent subtasks
**Solution**: Run independent tasks in parallel to reduce total time
**When to Use**: Independent or weakly coupled subtasks
**Related**: Feeds Task Decomposition

### [3.3 Hierarchical Pattern](./docs/patterns/orchestration/hierarchical.md)
**Tags**: `mature` `medium-complexity` `structured`
**Problem**: Flat groups struggle with coordination/load-balancing
**Solution**: Manager delegates tasks to workers and aggregates results
**When to Use**: Large task pools, heterogeneous expertise
**Related**: Leverages Lifecycle Management

### [3.4 Group Chat Pattern](./docs/patterns/orchestration/group-chat.md)
**Tags**: `emerging` `medium-complexity` `collaborative`
**Problem**: Unstructured chat can drift, loop, or explode in length
**Solution**: Agents collaborate via moderated conversational turns
**When to Use**: Open-ended design discussions, brainstorming
**Related**: Ties to Human-in-the-Loop and Reflection

### [3.5 Handoff Pattern](./docs/patterns/orchestration/handoff.md)
**Tags**: `emerging` `medium-complexity` `dynamic`
**Problem**: Single agent cannot cover all skills efficiently
**Solution**: Switch active agent by capability/context during task
**When to Use**: Multi-skill flows, compliance constraints
**Related**: Needs Registry and Capability Discovery

### [3.6 Market-Based Coordination Pattern](./docs/patterns/orchestration/market-based.md)
**Tags**: `experimental` `high-complexity` `distributed`
**Problem**: Central schedulers struggle with heterogeneous agents
**Solution**: Allocate tasks via bids based on utility/cost
**When to Use**: Heterogeneous costs/capabilities, elastic supply
**Related**: Combine with Version Negotiation

---

## Context Management Patterns
*Managing shared state, memory, and context*

### [4.1.1 Shared Memory Pattern](./docs/patterns/context/shared-memory.md)
**Tags**: `mature` `medium-complexity` `fundamental`
**Problem**: Agents duplicate state or drift when state is local-only
**Solution**: Central store for shared context with controlled access
**When to Use**: Any multi-agent context beyond trivial size
**Related**: Feeds Progressive Compression

### [4.1.2 Semantic Memory Pattern](./docs/patterns/context/semantic-memory.md)
**Tags**: `emerging` `medium-complexity` `knowledge`
**Problem**: Keyword search misses relevant knowledge
**Solution**: Store facts/concepts for semantic retrieval (embeddings/triples)
**When to Use**: Cross-domain knowledge needs, ambiguous queries
**Related**: Works with Shared Knowledge Store

### [4.1.3 Episodic Memory Pattern](./docs/patterns/context/episodic-memory.md)
**Tags**: `emerging` `medium-complexity` `experience`
**Problem**: Without episodes, agents lose history for continuity
**Solution**: Record interactions/events with timestamps and participants
**When to Use**: Conversational or longitudinal workflows
**Related**: Feeds Insight Distillation and Experience Replay

### [4.1.4 Procedural Memory Pattern](./docs/patterns/context/procedural-memory.md)
**Tags**: `emerging` `high-complexity` `skills`
**Problem**: Tacit skill remains trapped in prompts/scripts
**Solution**: Capture learned procedures/skills for reuse
**When to Use**: Recurring tasks with proven procedures
**Related**: Links to Continuous Fine-Tuning

### [4.2.1 Progressive Compression Pattern](./docs/patterns/context/progressive-compression.md)
**Tags**: `mature` `medium-complexity` `scalability`
**Problem**: Context windows/stores cannot grow without bounds
**Solution**: Summarise aging context recursively to retain signal
**When to Use**: Any long-running context stream
**Related**: Pairs with Selective Pruning

### [4.2.2 Selective Pruning Pattern](./docs/patterns/context/selective-pruning.md)
**Tags**: `mature` `medium-complexity` `efficiency`
**Problem**: Irrelevant data increases latency and cost
**Solution**: Remove irrelevant context via scores/policies
**When to Use**: Bounded budgets or latency targets
**Related**: Follows Progressive Compression

### [4.2.3 Insight Distillation Pattern](./docs/patterns/context/insight-distillation.md)
**Tags**: `emerging` `high-complexity` `intelligence`
**Problem**: Logs contain insight but little structure
**Solution**: Extract key decisions/rationales from raw interactions
**When to Use**: Mature systems with substantial logs
**Related**: Feeds Reflection Loop and Experience Replay

---

## Task Management Patterns
*Planning, decomposing, and managing agent tasks*

### [5.1 Task Decomposition Pattern](./docs/patterns/task/decomposition.md)
**Tags**: `mature` `medium-complexity` `planning`
**Problem**: Monolithic tasks hide dependencies and stall progress
**Solution**: Split complex goals into manageable subtasks
**When to Use**: Complex goals with obvious sub-steps
**Related**: Works with Concurrent Orchestration

### [5.2 Planning Pattern](./docs/patterns/task/planning.md)
**Tags**: `mature` `medium-complexity` `strategic`
**Problem**: Act-first approaches waste tokens/time
**Solution**: Form a plan before acting; revise as evidence arrives
**When to Use**: Expensive or high-risk tasks
**Related**: Feeds Reflection, Sequential Orchestration

### [5.3 Reflection Pattern](./docs/patterns/task/reflection.md)
**Tags**: `mature` `medium-complexity` `improvement`
**Problem**: Repeating same mistakes burns budget and trust
**Solution**: Self-critique outputs and adjust approach
**When to Use**: Any iterative generation or decision task
**Related**: Drives Reflection Loop (behavioral scale)

### [5.4 Tool Use Pattern](./docs/patterns/task/tool-use.md)
**Tags**: `mature` `low-complexity` `integration`
**Problem**: Re-implementing tools inside agents leads to duplication
**Solution**: Invoke external tools/APIs under policy
**When to Use**: Any external computation or data fetch
**Related**: See MCP, Zero-Trust

### [5.5 Capability Discovery Pattern](./docs/patterns/task/capability-discovery.md)
**Tags**: `emerging` `medium-complexity` `dynamic`
**Problem**: Name-based lookup misses best-fit skills
**Solution**: Discover/advertise capabilities dynamically
**When to Use**: Evolving ecosystems with many skills
**Related**: Builds on Registry · Feeds Handoff

---

## Knowledge Management Patterns
*Organizing and maintaining shared knowledge*

### [6.1 Two-Stage Knowledge Pipeline Pattern](./docs/patterns/knowledge/two-stage-pipeline.md)
**Tags**: `emerging` `high-complexity` `comprehensive`
**Problem**: Raw notes pile up; published knowledge lags
**Solution**: Manage granular findings and synthesised knowledge via two paths
**When to Use**: Teams that research continuously
**Related**: Works with Shared Knowledge Store and Insight Distillation

### [6.2.1 Shared Knowledge Store Pattern](./docs/patterns/knowledge/shared-store.md)
**Tags**: `emerging` `medium-complexity` `reuse`
**Problem**: Teams repeat research due to inaccessible prior work
**Solution**: Common repository supports fuzzy retrieval and structured access
**When to Use**: Any shared research/knowledge environment
**Related**: Pairs with Semantic Memory

---

## Human Integration Patterns
*Integrating human oversight and collaboration*

### [7.1 Human-in-the-Loop Pattern](./docs/patterns/human/human-in-loop.md)
**Tags**: `mature` `medium-complexity` `oversight`
**Problem**: Fully autonomous loops can drift or violate constraints
**Solution**: Humans approve, correct, or guide at key points
**When to Use**: High-risk outputs, regulated environments
**Related**: Integrates with Group Chat and Reflection

### [7.2 User Elicitation Pattern](./docs/patterns/human/user-elicitation.md)
**Tags**: `emerging` `medium-complexity` `clarification`
**Problem**: Vague inputs cause rework and poor outputs
**Solution**: System asks targeted questions to reduce ambiguity
**When to Use**: Ambiguous inputs and costly retries
**Related**: Pairs with Planning

### [7.3 Explainability Pattern](./docs/patterns/human/explainability.md)
**Tags**: `emerging` `high-complexity` `transparency`
**Problem**: Opaque agents undermine trust and debugging
**Solution**: Expose reasons, inputs, and limits of decisions
**When to Use**: Decision support and regulated outputs
**Related**: Leverages Event Sourcing for audit

### [7.4 Trust-Building Pattern](./docs/patterns/human/trust-building.md)
**Tags**: `emerging` `medium-complexity` `adoption`
**Problem**: Jumping to full autonomy spooks users
**Solution**: Increase autonomy gradually with transparency
**When to Use**: Any new autonomous capability
**Related**: Works with Reflection Loop

---

## System Quality Patterns
*Ensuring reliability, security, and observability*

### [8.1.1 Resilient Communication Pattern](./docs/patterns/quality/resilient-communication.md)
**Tags**: `mature` `high-complexity` `reliability`
**Problem**: Networks and components fail unpredictably
**Solution**: Communication layer tolerates faults via retries/failover
**When to Use**: Any critical path
**Related**: Relies on Transport

### [8.2 Observability Pattern](./docs/patterns/quality/observability.md)
**Tags**: `emerging` `medium-complexity` `diagnostics`
**Problem**: Without visibility, incident response drags
**Solution**: Tracing, metrics, logs deliver runtime insight
**When to Use**: Always—start day one
**Related**: Uses Standardised Message Format

### [8.3.1 Identity Propagation Pattern](./docs/patterns/quality/identity-propagation.md)
**Tags**: `emerging` `medium-complexity` `security`
**Problem**: Lost identity breaks auditing and least-privilege
**Solution**: Carry caller identity/scope across agent hops
**When to Use**: Any multi-hop call chain
**Related**: Pairs with Zero-Trust Boundary

### [8.3.2 Encrypted Message Bus Pattern](./docs/patterns/quality/encrypted-bus.md)
**Tags**: `emerging` `medium-complexity` `security`
**Problem**: Unencrypted channels expose sensitive data
**Solution**: Encrypt data in transit across transport
**When to Use**: Always for non-public data
**Related**: Works with Transport, Message Format

### [8.3.3 Zero-Trust Boundary Pattern](./docs/patterns/quality/zero-trust.md)
**Tags**: `emerging` `high-complexity` `security`
**Problem**: Implicit trust enables lateral movement
**Solution**: Authenticate/authorise every call
**When to Use**: Any environment with sensitive data
**Related**: Requires Identity Propagation

### [8.4 Version Negotiation Pattern](./docs/patterns/quality/version-negotiation.md)
**Tags**: `emerging` `medium-complexity` `interoperability`
**Problem**: Lock-step upgrades cause outages
**Solution**: Coexist old/new formats; upgrade gracefully
**When to Use**: Multi-team, rolling upgrade environments
**Related**: Integrates with A2A and Message Format

### [8.5 Configuration-Driven Capabilities Pattern](./docs/patterns/quality/config-driven.md)
**Tags**: `emerging` `medium-complexity` `flexibility`
**Problem**: Code pushes for toggles slow iteration
**Solution**: Enable/disable capabilities via config
**When to Use**: Feature rollout and rapid experimentation
**Related**: Pairs with Observability

### [8.6 Standardised Message Format Pattern](./docs/patterns/quality/message-format.md)
**Tags**: `mature` `low-complexity` `interoperability`
**Problem**: Inconsistent payloads block routing
**Solution**: Consistent envelopes enable interop
**When to Use**: Immediately—do not delay
**Related**: Foundational for A2A, Transport

### [8.7 Event Sourcing Pattern](./docs/patterns/quality/event-sourcing.md)
**Tags**: `mature` `high-complexity` `auditability`
**Problem**: State snapshots lose history
**Solution**: Persist events as truth; rebuild by replay
**When to Use**: High-audit domains, recovery needs
**Related**: Supports EDA, Explainability

---

## Self-Improvement Patterns
*Learning and adaptation mechanisms*

### [9.1 Reflection Loop](./docs/patterns/improvement/reflection-loop.md)
**Tags**: `mature` `medium-complexity` `behavioural`
**Solution**: Apply reflection continually to improve over time
**Related**: See Reflection Pattern (5.3)

### [9.2 Social Learning Pattern](./docs/patterns/improvement/social-learning.md)
**Tags**: `emerging` `medium-complexity`
**Solution**: Agents observe peers and adopt winning strategies

### [9.3 Experience Replay Pattern](./docs/patterns/improvement/experience-replay.md)
**Tags**: `emerging` `medium-complexity`
**Solution**: Sample past interactions to refine prompts/models

### [9.4 Evolutionary Population Pattern](./docs/patterns/improvement/evolutionary.md)
**Tags**: `experimental` `high-complexity`
**Solution**: Maintain population; evolve via selection/mutation

### [9.5 Continuous Fine-Tuning Pattern](./docs/patterns/improvement/fine-tuning.md)
**Tags**: `mature` `high-complexity`
**Solution**: Apply small weight updates during service

### [9.6 Reward-Shaping Feedback Pattern](./docs/patterns/improvement/reward-shaping.md)
**Tags**: `emerging` `medium-complexity`
**Solution**: Use human/heuristic rewards to steer behavior

### [9.7 Safety-Guard Adaptation Pattern](./docs/patterns/improvement/safety-guard.md)
**Tags**: `experimental` `medium-complexity` `safety`
**Solution**: Guards adjust thresholds using violation logs

---

## Quick Stats
- **Total Patterns**: 53
- **Mature**: 18 | **Emerging**: 27 | **Experimental**: 8
- **Low Complexity**: 5 | **Medium**: 38 | **High**: 10

## Pattern Selection Guide
Not sure which pattern to use? Try our [Pattern Selector Tool](../tools/pattern-selector.html) or check the [Pattern Browser](../tools/pattern-browser.html).