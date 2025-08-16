## 🖼 System Architecture

```mermaid
flowchart TD
    A[User Input: Text or Image] --> B[Streamlit UI]
    B --> C[Security Layer: Sanitize and Safety Check]
    C --> D{Image Provided?}

    D -->|Yes| E[Image Classifier Dummy Function]
    D -->|No| F[Skip Image Classification]

    E --> G[LLM via LangChain Azure OpenAI]
    F --> G

    G --> H[Schema Validation and Retry if Invalid]
    H --> I[Show JSON and Image in UI]
    I --> J[Download JSON]
    I --> K[Validate Email]
    K --> L[Send JSON and Image via SMTP]
