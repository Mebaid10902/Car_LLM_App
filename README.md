## 🖼 System Architecture

```mermaid
flowchart TD
    A[User Input<br/>Text or Image] --> B[Streamlit UI]
    B --> C[Security Layer<br/>(Sanitize + Safety Check)]
    C --> D{Image Provided?}

    D -->|Yes| E[Image Classifier<br/>(Dummy Function)]
    D -->|No| F[Skip Image Classification]

    E --> G[LLM via LangChain<br/>Azure OpenAI]
    F --> G

    G --> H[Schema Validation<br/>+ Retry if Invalid]
    H --> I[Show JSON + Image in UI]
    I --> J[Download JSON]
    I --> K[Validate Email]
    K --> L[Send JSON + Image via SMTP]

---
