"""
Agentic Patterns Library - Example Implementation
Demonstrates Agent Registry + Message Transport + Hierarchical Orchestration
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Foundation Pattern: Agent Registry (Pattern 1.1)
# ============================================================================

@dataclass
class AgentCapability:
    """Describes what an agent can do"""
    name: str
    version: str
    constraints: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class AgentRegistration:
    """Agent registration record"""
    agent_id: str
    capabilities: List[AgentCapability]
    endpoint: str
    health_endpoint: str
    registered_at: datetime
    last_heartbeat: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentRegistry:
    """
    Central registry for agent discovery and management.
    Implements Pattern 1.1: Agent Registry Pattern
    """

    def __init__(self):
        self._agents: Dict[str, AgentRegistration] = {}
        self._capability_index: Dict[str, List[str]] = {}

    def register(self, agent_id: str, capabilities: List[AgentCapability],
                 endpoint: str, metadata: Optional[Dict] = None) -> bool:
        """Register an agent with its capabilities"""
        registration = AgentRegistration(
            agent_id=agent_id,
            capabilities=capabilities,
            endpoint=endpoint,
            health_endpoint=f"{endpoint}/health",
            registered_at=datetime.now(),
            last_heartbeat=datetime.now(),
            metadata=metadata or {}
        )

        self._agents[agent_id] = registration

        # Update capability index
        for capability in capabilities:
            if capability.name not in self._capability_index:
                self._capability_index[capability.name] = []
            self._capability_index[capability.name].append(agent_id)

        logger.info(f"Registered agent {agent_id} with capabilities: {[c.name for c in capabilities]}")
        return True

    def discover(self, capability: str, constraints: Optional[Dict] = None) -> List[AgentRegistration]:
        """Discover agents by capability"""
        if capability not in self._capability_index:
            return []

        agent_ids = self._capability_index[capability]
        agents = [self._agents[aid] for aid in agent_ids if aid in self._agents]

        # Apply constraints if provided
        if constraints:
            agents = [a for a in agents if self._matches_constraints(a, constraints)]

        return agents

    def _matches_constraints(self, agent: AgentRegistration, constraints: Dict) -> bool:
        """Check if agent matches given constraints"""
        for cap in agent.capabilities:
            if all(cap.constraints.get(k) == v for k, v in constraints.items()):
                return True
        return False


# ============================================================================
# Foundation Pattern: Message Transport (Pattern 1.2)
# ============================================================================

class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    COMMAND = "command"


@dataclass
class Message:
    """Standard message envelope"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = MessageType.REQUEST
    source: str = ""
    destination: str = ""
    payload: Any = None
    correlation_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    headers: Dict[str, Any] = field(default_factory=dict)


class MessageBus:
    """
    Asynchronous message bus for agent communication.
    Implements Pattern 1.2: Message Transport Pattern
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._queues: Dict[str, asyncio.Queue] = {}

    async def publish(self, topic: str, message: Message) -> None:
        """Publish message to a topic"""
        logger.info(f"Publishing to {topic}: {message.id}")

        if topic in self._subscribers:
            for subscriber in self._subscribers[topic]:
                await subscriber(message)

        if topic in self._queues:
            await self._queues[topic].put(message)

    def subscribe(self, topic: str, callback: Callable) -> None:
        """Subscribe to a topic with a callback"""
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(callback)
        logger.info(f"Subscribed to {topic}")

    async def create_queue(self, topic: str) -> asyncio.Queue:
        """Create a queue for a topic"""
        if topic not in self._queues:
            self._queues[topic] = asyncio.Queue()
        return self._queues[topic]


# ============================================================================
# Orchestration Pattern: Hierarchical Pattern (Pattern 3.3)
# ============================================================================

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """Task to be executed by workers"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    payload: Any = None
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None


class Worker:
    """Worker agent that executes tasks"""

    def __init__(self, worker_id: str, capabilities: List[str]):
        self.id = worker_id
        self.capabilities = capabilities
        self.current_task: Optional[Task] = None

    async def execute(self, task: Task) -> Task:
        """Execute a task"""
        logger.info(f"Worker {self.id} executing task {task.id}")
        self.current_task = task
        task.status = TaskStatus.IN_PROGRESS

        try:
            # Simulate work
            await asyncio.sleep(1)

            # Process based on task type
            if task.name == "research":
                task.result = {"findings": f"Research completed by {self.id}"}
            elif task.name == "analysis":
                task.result = {"analysis": f"Analysis performed by {self.id}"}
            else:
                task.result = {"output": f"Task {task.name} completed by {self.id}"}

            task.status = TaskStatus.COMPLETED

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)

        self.current_task = None
        return task


class HierarchicalOrchestrator:
    """
    Manager agent that delegates tasks to workers.
    Implements Pattern 3.3: Hierarchical Pattern
    """

    def __init__(self, registry: AgentRegistry, message_bus: MessageBus):
        self.registry = registry
        self.message_bus = message_bus
        self.workers: List[Worker] = []
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.results: Dict[str, Task] = {}

    def add_worker(self, worker: Worker) -> None:
        """Add a worker to the pool"""
        self.workers.append(worker)
        # Register worker in the registry
        capabilities = [AgentCapability(name=cap, version="1.0") for cap in worker.capabilities]
        self.registry.register(
            agent_id=worker.id,
            capabilities=capabilities,
            endpoint=f"worker://{worker.id}"
        )

    async def execute_workflow(self, tasks: List[Task]) -> List[Task]:
        """Execute a workflow by distributing tasks to workers"""
        logger.info(f"Starting workflow with {len(tasks)} tasks")

        # Queue all tasks
        for task in tasks:
            await self.task_queue.put(task)

        # Create worker tasks
        worker_tasks = []
        for worker in self.workers:
            worker_task = asyncio.create_task(self._worker_loop(worker))
            worker_tasks.append(worker_task)

        # Wait for all tasks to complete
        while not self.task_queue.empty() or any(w.current_task for w in self.workers):
            await asyncio.sleep(0.1)

        # Cancel worker loops
        for wt in worker_tasks:
            wt.cancel()

        # Collect results
        completed_tasks = list(self.results.values())
        logger.info(f"Workflow completed: {len(completed_tasks)} tasks processed")

        return completed_tasks

    async def _worker_loop(self, worker: Worker) -> None:
        """Worker processing loop"""
        while True:
            try:
                # Get task from queue
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)

                # Check if worker can handle this task
                if task.name in worker.capabilities:
                    task.assigned_to = worker.id

                    # Notify task assignment
                    await self.message_bus.publish(
                        "task.assigned",
                        Message(
                            type=MessageType.EVENT,
                            source="orchestrator",
                            destination=worker.id,
                            payload={"task_id": task.id, "worker_id": worker.id}
                        )
                    )

                    # Execute task
                    result = await worker.execute(task)
                    self.results[task.id] = result

                    # Notify task completion
                    await self.message_bus.publish(
                        "task.completed",
                        Message(
                            type=MessageType.EVENT,
                            source=worker.id,
                            destination="orchestrator",
                            payload={"task_id": task.id, "status": result.status.value}
                        )
                    )
                else:
                    # Put task back if worker can't handle it
                    await self.task_queue.put(task)
                    await asyncio.sleep(0.1)

            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break


# ============================================================================
# Example Usage: Multi-Agent Research System
# ============================================================================

async def main():
    """Demonstrate a multi-agent research system using multiple patterns"""

    # Initialize infrastructure
    registry = AgentRegistry()
    message_bus = MessageBus()
    orchestrator = HierarchicalOrchestrator(registry, message_bus)

    # Set up message monitoring
    async def log_events(message: Message):
        logger.info(f"Event: {message.payload}")

    message_bus.subscribe("task.assigned", log_events)
    message_bus.subscribe("task.completed", log_events)

    # Create specialized workers
    research_worker = Worker("researcher-001", ["research", "web_search"])
    analysis_worker = Worker("analyst-001", ["analysis", "summarization"])
    report_worker = Worker("reporter-001", ["reporting", "formatting"])

    # Add workers to orchestrator
    orchestrator.add_worker(research_worker)
    orchestrator.add_worker(analysis_worker)
    orchestrator.add_worker(report_worker)

    # Discover available capabilities
    print("\n=== Available Capabilities ===")
    for capability in ["research", "analysis", "reporting"]:
        agents = registry.discover(capability)
        print(f"{capability}: {[a.agent_id for a in agents]}")

    # Create workflow tasks
    workflow_tasks = [
        Task(name="research", payload={"query": "AI agent patterns"}),
        Task(name="research", payload={"query": "multi-agent systems"}),
        Task(name="analysis", payload={"data": "research_output"}),
        Task(name="reporting", payload={"format": "markdown"}),
    ]

    # Execute workflow
    print("\n=== Executing Workflow ===")
    results = await orchestrator.execute_workflow(workflow_tasks)

    # Display results
    print("\n=== Workflow Results ===")
    for task in results:
        print(f"Task {task.name}: {task.status.value}")
        if task.result:
            print(f"  Result: {task.result}")
        if task.error:
            print(f"  Error: {task.error}")


if __name__ == "__main__":
    asyncio.run(main())