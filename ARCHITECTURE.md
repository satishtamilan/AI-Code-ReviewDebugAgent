# AI Code Review Agent - Architecture Diagrams

## System Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        UI[Web UI - Flask/HTML/CSS/JS]
        CLI[Command Line Interface]
        API[REST API Endpoints]
    end
    
    subgraph "Application Layer"
        APP[app_ui.py - Flask App]
        CODEBASE[codebase_analyzer.py]
        DEMO[demo_pure_google.py]
    end
    
    subgraph "Agent Core - Multi-Agent System"
        ORCH[Multi-Agent Orchestrator]
        REV[Code Review Agent]
        DEBUG[Debug Agent]
        FIX[Fix Agent]
    end
    
    subgraph "Tools Layer"
        SYNTAX[Syntax Checker Tool]
        COMPLEX[Complexity Analyzer]
        SECURITY[Security Scanner]
        PYLINT[Pylint Tool]
        GCODE[Google Code Execution]
        MCP[MCP Tool Adapter]
    end
    
    subgraph "Memory & State"
        SESSION[Session Manager]
        MEMORY[Memory Bank]
        CONTEXT[Context Engineering]
    end
    
    subgraph "Observability"
        TRACE[AgentTracer]
        METRICS[Metrics Collector]
        LOGS[Logging System]
    end
    
    subgraph "External Services"
        GEMINI[Google Gemini 2.5 Flash API]
        SANDBOX[Google Cloud Sandbox]
        MCPSERV[MCP Servers]
    end
    
    UI --> APP
    CLI --> CODEBASE
    API --> APP
    
    APP --> ORCH
    CODEBASE --> ORCH
    DEMO --> ORCH
    
    ORCH --> REV
    ORCH --> DEBUG
    ORCH --> FIX
    
    REV --> SYNTAX
    REV --> COMPLEX
    REV --> SECURITY
    REV --> PYLINT
    DEBUG --> GCODE
    FIX --> MCP
    
    ORCH --> SESSION
    ORCH --> MEMORY
    ORCH --> CONTEXT
    
    ORCH --> TRACE
    ORCH --> METRICS
    ORCH --> LOGS
    
    REV --> GEMINI
    DEBUG --> GEMINI
    FIX --> GEMINI
    GCODE --> SANDBOX
    MCP --> MCPSERV
    
    SESSION -.-> STORAGE[(JSON Storage)]
    MEMORY -.-> STORAGE
    TRACE -.-> STORAGE
    
    style GEMINI fill:#4285F4
    style SANDBOX fill:#4285F4
    style MCPSERV fill:#4285F4
```

## Multi-Agent Workflow

```mermaid
sequenceDiagram
    participant User
    participant UI as Web UI
    participant Orch as Orchestrator
    participant Rev as Review Agent
    participant Debug as Debug Agent
    participant Fix as Fix Agent
    participant Gemini as Google Gemini
    participant Session as Session Manager
    participant Memory as Memory Bank
    
    User->>UI: Submit Code
    UI->>Orch: Analyze Request
    
    activate Orch
    Orch->>Session: Create Session
    Orch->>Rev: Sequential Step 1
    
    activate Rev
    Rev->>Gemini: Review Code
    Gemini-->>Rev: Analysis Results
    Rev->>Memory: Store Patterns
    Rev-->>Orch: Issues Found
    deactivate Rev
    
    Orch->>Debug: Sequential Step 2
    activate Debug
    Debug->>Gemini: Debug Code
    Gemini-->>Debug: Root Causes
    Debug-->>Orch: Debug Info
    deactivate Debug
    
    Orch->>Fix: Sequential Step 3
    activate Fix
    Fix->>Gemini: Generate Fixes
    Gemini-->>Fix: Fixed Code
    Fix-->>Orch: Fixes Applied
    deactivate Fix
    
    Orch->>Session: Save Results
    Orch-->>UI: Complete Analysis
    deactivate Orch
    
    UI-->>User: Display Results
```

## Data Flow - Single File Analysis

```mermaid
flowchart LR
    A[User Pastes Code] --> B[Language Detection]
    B --> C[Code Validation]
    C --> D{Valid?}
    D -->|No| E[Show Error]
    D -->|Yes| F[Create Session]
    
    F --> G[Start Trace]
    G --> H[Syntax Check]
    H --> I[Security Scan]
    I --> J[Complexity Analysis]
    J --> K[Gemini Review]
    
    K --> L[Parse Results]
    L --> M[Store in Memory]
    M --> N[End Trace]
    N --> O[Record Metrics]
    O --> P[Display Results]
    
    P --> Q[Save Session]
    Q --> R[Generate Report]
    
    style K fill:#4285F4
    style M fill:#90EE90
    style O fill:#FFD700
```

## Data Flow - Codebase Analysis

```mermaid
flowchart TD
    A[User Enters Directory Path] --> B[Scan Directory]
    B --> C[Filter Files by Extension]
    C --> D[Create File List]
    
    D --> E{For Each File}
    
    E --> F1[File 1: Analyze]
    E --> F2[File 2: Analyze]
    E --> F3[File N: Analyze]
    
    F1 --> G1[Detect Language]
    F2 --> G2[Detect Language]
    F3 --> G3[Detect Language]
    
    G1 --> H1[Call Gemini]
    G2 --> H2[Call Gemini]
    G3 --> H3[Call Gemini]
    
    H1 --> I[Aggregate Results]
    H2 --> I
    H3 --> I
    
    I --> J[Calculate Statistics]
    J --> K[Severity Breakdown]
    J --> L[Issue Types]
    J --> M[Language Stats]
    
    K --> N[Generate Report]
    L --> N
    M --> N
    
    N --> O[Save to Markdown]
    O --> P[Export Traces]
    P --> Q[Store in Memory]
    Q --> R[Display in UI]
    
    style H1 fill:#4285F4
    style H2 fill:#4285F4
    style H3 fill:#4285F4
```

## Component Architecture

```mermaid
graph TB
    subgraph "Presentation Layer"
        WEB[Web UI - templates/index.html]
        SHELL[Shell Scripts - .sh files]
    end
    
    subgraph "Business Logic Layer"
        subgraph "Agent System"
            MULTI[multi_agent_orchestrator.py]
            REVIEW[code_reviewer.py]
            DEBUGGER[debugger.py]
            GEMINI_INT[gemini_integration.py]
        end
        
        subgraph "Tools & Utilities"
            TOOLS[tools.py - 4 Analysis Tools]
            MCP_CLIENT[mcp_client.py]
            UTILS[utils.py]
        end
        
        subgraph "State Management"
            SESS[session_manager.py]
            MEM[Memory Bank]
            CTX[context_engineering.py]
        end
        
        subgraph "Observability Layer"
            OBS[observability.py]
            TRACER[AgentTracer]
            METER[MetricsCollector]
        end
    end
    
    subgraph "Data Layer"
        JSON_SESS[.live_sessions/*.json]
        JSON_MEM[.live_memory/memories.json]
        JSON_TRACE[.live_traces/*.json]
        REPORTS[*.md Reports]
    end
    
    WEB --> MULTI
    SHELL --> MULTI
    
    MULTI --> REVIEW
    MULTI --> DEBUGGER
    REVIEW --> GEMINI_INT
    DEBUGGER --> GEMINI_INT
    
    MULTI --> TOOLS
    MULTI --> MCP_CLIENT
    
    MULTI --> SESS
    MULTI --> CTX
    SESS --> MEM
    
    MULTI --> OBS
    OBS --> TRACER
    OBS --> METER
    
    SESS --> JSON_SESS
    MEM --> JSON_MEM
    TRACER --> JSON_TRACE
    MULTI --> REPORTS
    
    GEMINI_INT -.->|API Calls| GEMINI_API[Google Gemini API]
    
    style GEMINI_API fill:#4285F4
```

## Session & Memory Flow

```mermaid
stateDiagram-v2
    [*] --> SessionCreated: User Request
    SessionCreated --> CodeAnalysis: Start Analysis
    
    state CodeAnalysis {
        [*] --> Reviewing
        Reviewing --> Debugging
        Debugging --> Fixing
        Fixing --> [*]
    }
    
    CodeAnalysis --> StoreInteraction: Save Each Step
    StoreInteraction --> UpdateContext: Update State
    
    UpdateContext --> CheckPatterns: Analyze Results
    CheckPatterns --> StoreMemory: Found Pattern
    CheckPatterns --> SessionComplete: No Pattern
    
    StoreMemory --> SessionComplete
    SessionComplete --> PersistSession: Save to Disk
    PersistSession --> [*]
    
    note right of StoreMemory
        Stores in Memory Bank:
        - Common Bugs
        - Code Patterns
        - Fix Strategies
    end note
```

## Observability Flow

```mermaid
flowchart LR
    A[Operation Start] --> B[Create Trace Span]
    B --> C[Add Attributes]
    C --> D[Execute Operation]
    
    D --> E[Log Events]
    D --> F[Record Metrics]
    
    E --> G[Span Event 1]
    E --> H[Span Event 2]
    
    F --> I[Counter: +1]
    F --> J[Timing: Duration]
    F --> K[Value: Score]
    
    G --> L[End Span]
    H --> L
    I --> L
    J --> L
    K --> L
    
    L --> M[Calculate Duration]
    M --> N[Export Traces]
    M --> O[Export Metrics]
    
    N --> P[JSON File]
    O --> Q[JSON File]
    
    style B fill:#FFD700
    style F fill:#FFD700
    style N fill:#90EE90
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        BROWSER[Web Browser]
        CURL[cURL/API Clients]
        TERMINAL[Terminal/CLI]
    end
    
    subgraph "Application Server"
        FLASK[Flask App :5001]
        WORKER[Background Workers]
    end
    
    subgraph "Agent Core"
        AGENTS[Agent System]
        TOOLS_SYS[Tools System]
        STORAGE_SYS[Storage System]
    end
    
    subgraph "External APIs"
        GEMINI_EXT[Google Gemini API]
        SANDBOX_EXT[Google Cloud Sandbox]
    end
    
    subgraph "Data Storage"
        FILES[Local JSON Files]
        REPORTS_STORE[Markdown Reports]
    end
    
    subgraph "Optional: Cloud Deployment"
        GCR[Google Cloud Run]
        GSM[Google Secret Manager]
        GCM[Google Cloud Monitoring]
    end
    
    BROWSER --> FLASK
    CURL --> FLASK
    TERMINAL --> AGENTS
    
    FLASK --> AGENTS
    AGENTS --> TOOLS_SYS
    AGENTS --> STORAGE_SYS
    
    AGENTS --> GEMINI_EXT
    TOOLS_SYS --> SANDBOX_EXT
    
    STORAGE_SYS --> FILES
    AGENTS --> REPORTS_STORE
    
    FLASK -.->|Deploy| GCR
    GCR -.-> GSM
    GCR -.-> GCM
    
    style GEMINI_EXT fill:#4285F4
    style SANDBOX_EXT fill:#4285F4
    style GCR fill:#4285F4
    style GSM fill:#4285F4
    style GCM fill:#4285F4
```

## Technology Stack

```mermaid
mindmap
  root((AI Code Review Agent))
    Frontend
      HTML5
      CSS3
      JavaScript ES6+
      Fetch API
    Backend
      Python 3.9+
      Flask
      Flask-CORS
    AI & ML
      Google Gemini 2.5 Flash
      google-generativeai SDK
    Analysis Tools
      AST Parser
      Pylint
      Custom Security Scanner
      Complexity Analyzer
    Storage
      JSON Files
      File System
    Observability
      Custom Tracer
      Metrics Collector
      Logging
    Protocols
      MCP Model Context Protocol
      REST API
      HTTP/HTTPS
    Deployment
      Google Cloud Run
      Docker
      Gunicorn
```

## Request Processing Flow

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant Flask
    participant Orchestrator
    participant Tools
    participant Gemini
    participant Storage
    
    Client->>Flask: POST /api/analyze
    Flask->>Orchestrator: analyze_code(code, language)
    
    activate Orchestrator
    Orchestrator->>Storage: Create Session
    Orchestrator->>Storage: Start Trace
    
    par Parallel Tool Execution
        Orchestrator->>Tools: Syntax Check
        Orchestrator->>Tools: Security Scan
        Orchestrator->>Tools: Complexity Analysis
    end
    
    Tools-->>Orchestrator: Tool Results
    
    Orchestrator->>Gemini: Review with Context
    Gemini-->>Orchestrator: AI Analysis
    
    Orchestrator->>Storage: Save Interaction
    Orchestrator->>Storage: Store Patterns
    Orchestrator->>Storage: End Trace
    Orchestrator->>Storage: Record Metrics
    
    Orchestrator-->>Flask: Complete Results
    deactivate Orchestrator
    
    Flask-->>Client: JSON Response
```

## File Structure

```mermaid
graph LR
    ROOT[kaggle-genai/] --> AGENT[agent/]
    ROOT --> TEMPLATES[templates/]
    ROOT --> TESTS[tests/]
    ROOT --> DOCS[docs/]
    ROOT --> NOTEBOOKS[notebooks/]
    
    AGENT --> A1[multi_agent_orchestrator.py]
    AGENT --> A2[code_reviewer.py]
    AGENT --> A3[tools.py]
    AGENT --> A4[session_manager.py]
    AGENT --> A5[observability.py]
    AGENT --> A6[context_engineering.py]
    AGENT --> A7[mcp_client.py]
    AGENT --> A8[gemini_integration.py]
    
    TEMPLATES --> T1[index.html]
    
    ROOT --> APP[app_ui.py]
    ROOT --> CODEBASE[codebase_analyzer.py]
    ROOT --> CONFIG[config.py]
    ROOT --> REQ[requirements.txt]
    ROOT --> README[README.md]
    
    style AGENT fill:#90EE90
    style TEMPLATES fill:#FFB6C1
    style APP fill:#87CEEB
```

