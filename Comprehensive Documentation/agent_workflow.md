# 🤖 AI Agent Reasoning Workflow

This flowchart illustrates the step-by-step logic used by the **Security Analyst Agent (Qwen3)** when processing a new observation from the drone's Vision model.

```mermaid
flowchart TD
    Start[New VLM Description Received] --> Step1[Call Tool: evaluate_alert_rules]
    Step1 --> CheckAlerts{Did rules trigger?}
    
    CheckAlerts -- YES --> Step2[Call Tool: search_frame_history]
    Step2 --> Step3[Analyze Patterns & Recurrence]
    
    CheckAlerts -- NO --> Step3
    
    Step3 --> Step4[Calculate Final Threat Level]
    
    Step4 --> CheckThreat{Threat > LOW?}
    
    CheckThreat -- YES --> Step5[Determine Recommended Action]
    CheckThreat -- NO --> Step6[Fact-check with History]
    
    Step5 --> Final[Call Tool: log_security_event]
    Step6 --> Final
    
    Final --> End[Broadcast Event to Dashboard]
    
    style Start fill:#f9f,stroke:#333,stroke-width:2px
    style Final fill:#00d2ff,stroke:#333,stroke-width:2px
    style CheckAlerts fill:#ff9f43,stroke:#333,stroke-width:2px
```

### **Reasoning Stages:**
1.  **Perception Processing:** The agent receives a natural language description (e.g., *"A red sedan is parked in front of the main gate"*).
2.  **Tool Orchestration:** The agent doesn't just guess; it uses `evaluate_alert_rules` to check against deterministic security parameters.
3.  **Temporal Context:** It uses `search_frame_history` to see if this object has been seen before. This allows the agent to distinguish between a "Delivery" (seen once) and "Loitering" (seen multiple times).
4.  **Actionable Intelligence:** The final output isn't just data—it's a recommendation (e.g., *"Dispatch security personnel for ID check"*).
