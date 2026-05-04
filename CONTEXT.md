# Omnius Context

Omnius is an automated media intelligence platform that implements Robert Entman's framing methodology to analyze news narratives.

## Domain Language

### Core Methodology
- **Entman's Methodology**: A theoretical framework for news analysis that identifies how media outlets frame issues.
- **Framing Pillars**: The four components of a frame:
    - **Problem Definition**: Identification of the core issue.
    - **Causal Interpretation**: Attributing blame or cause.
    - **Moral Evaluation**: Judging the actors and actions.
    - **Treatment Recommendation**: Proposing solutions or paths forward.

### System Components
- **Research Agent**: An autonomous AI agent powered by Pydantic AI that searches and filters news articles.
- **Analysis Pipeline**: A multi-stage process that scrapes articles and applies framing analysis via LLMs.
- **Narrative Network Matrix**: An interactive graph visualization (D3.js) showing relationships between different news sources.
- **Shared Nucleus**: The central keywords or themes that connect disparate news frames in the visualization.
- **Intelligence Report**: A synthesized summary of commonalities and discrepancies between sources.

### Security & Infrastructure
- **X-API-Key**: A custom header-based authentication mechanism used to protect sensitive API endpoints (`/api/analyze`, `/api/research`).
- **CORS (Cross-Origin Resource Sharing)**: Security policy enforced on the backend to restrict access only to the Netlify frontend and local development environments.
- **Azure Container Registry (ACR)**: Private registry for storing production backend Docker images.
- **Azure App Service (AAS)**: Linux-based hosting for the FastAPI backend container.
- **Netlify**: Global CDN for hosting the React frontend.
- **Managed Identity**: Security mechanism (AcrPull) for AAS to pull images from ACR without hardcoded credentials.
- **SSE (Server-Sent Events)**: A streaming protocol used by the Analysis Pipeline to provide real-time updates to the frontend during the framing process.
- **Cold Start**: A delay occurring when an idle container is restarted on Azure App Service (Free Tier), often causing the first request to be slow or fail.
