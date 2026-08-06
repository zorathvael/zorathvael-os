# Zorathvael OS — Architecture Documentation

## Overview
Zorathvael OS is designed around the core principle: **"One Core. Many Interfaces."** The system abstracts intelligence and workflow orchestration into a unified core, allowing it to scale seamlessly across Android, Desktop, and Server environments without altering its underlying architecture.

## Core Architecture Components

```
+---------------------------------------------------------------+
|                        Zorathvael Core                        |
|  +--------------+  +---------------+  +--------------------+  |
|  |   AI Router  |  | Memory Engine |  |  Workflow Engine   |  |
|  +--------------+  +---------------+  +--------------------+  |
|  +--------------+  +---------------+  +--------------------+  |
|  | Automation   |  | Integration   |  |   Report Engine    |  |
|  +--------------+  +---------------+  +--------------------+  |
+---------------------------------------------------------------+
         |                  |                  |
    [Android]          [Desktop]          [Server]
```

### 1. AI Router (`ai_router.py`)
Acts as the intelligent dispatcher, routing tasks to specialized AI models based on department classification (e.g., Command Center -> OpenAI, Research -> Gemini, Documentation -> Claude, Engineering -> DeepSeek).

### 2. Memory Engine (`memory_engine.py`)
Manages both short-term execution state and long-term persistent storage (vector & relational databases), ensuring context retention across multi-step workflows.

### 3. Workflow Engine (`workflow_engine.py`)
Orchestrates complex, multi-step agentic execution graphs, chaining AI tasks, memory operations, and integrations deterministically.

### 4. Automation & Integration Engines
Handles external event triggers, webhook integrations, and platform-specific automation (such as MacroDroid on Android).
