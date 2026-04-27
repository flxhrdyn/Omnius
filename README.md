<div align="center">

  # Omnius — Automated Media Intelligence
  **Automated Framing Analysis using Robert Entman's Methodology & LLM Intelligence.**
  
  [![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
  [![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
  [![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
  [![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
  [![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
  [![Groq](https://img.shields.io/badge/Groq_Cloud-F55036?style=for-the-badge&logo=ai&logoColor=white)](https://console.groq.com/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
</div>

---

## Overview

**Omnius** is a professional media intelligence platform that implements **Robert Entman's (1993)** framing theory to automatically dissect online news narratives. 

In an era of information warfare and systemic bias, Omnius provides a "truth-telling" lens that transforms static news text into deep analytical insights. It identifies how media outlets define problems, interpret causes, make moral evaluations, and recommend treatments across different sources.

## Core Features

- **Automated Framing Intelligence**: Identifies Robert Entman's 4 framing pillars using state-of-the-art LLMs (Llama 3.3, 3.1, and Qwen).
- **Comparative Synthesis**: Generates high-level intelligence reports that find common ground and key discrepancies between different media outlets.
- **Narrative Network Matrix**: Interactive **D3.js-powered** graph visualization that reveals the "Shared Nucleus" of keywords connecting different sources.
- **Bias Intelligence Indicator**: Real-time sentiment and bias detection across media actors and overall article tone.
- **Sleek Intelligence Workspace**: A modern, dark-themed dashboard inspired by high-end intelligence tools, featuring smooth transitions and professional typography.
- **Model Configurator**: Hot-swap between different LLM engines (Llama, Qwen) to adjust analysis depth and speed.

## Technology Stack

### Backend (Python & FastAPI)
- **Framework**: FastAPI (Asynchronous High-Performance API)
- **Web Server**: Uvicorn with Gunicorn support
- **LLM Orchestration**: Groq SDK (Llama 3.3-70B, Llama 3.1-8B, Qwen 3 32B)
- **NLP & Language**: Langdetect (Automatic article language identification)
- **Scraping Engine**: BeautifulSoup4 with **lxml** parser & Requests
- **Data Modeling**: Pydantic v2 (Strict schema and data integrity)

### Frontend (React & TypeScript)
- **Framework**: **React 19** with **Vite 6**
- **Language**: TypeScript (Strictly typed architecture)
- **Styling**: **Tailwind CSS v4** & **Motion v12** (Fluid animations)
- **Routing**: **React Router v7** (Decoupled navigation)
- **Visualization**: **D3.js** (Dynamic Network Graphs), **Recharts** (Bias Indicators)
- **Content Rendering**: **React Markdown** (LLM Synthesis display)
- **Networking**: Axios (Async HTTP requests)
- **Icons**: Lucide React

### Deployment & DevOps
- **Containerization**: Docker with **uv** (Ultra-fast Python package installer)
- **Runtime**: Node.js 22 (Frontend) & Python 3.12 (Backend)
- **Architecture**: Decoupled Monorepo (Independent Frontend & Backend)

## System Architecture

```mermaid
graph TD
    subgraph UI_Layer [Frontend - React]
        Landing[Landing Page] --> Workspace[Analysis Workspace]
        Workspace --> Config[Model Configuration]
        Workspace --> Result[Intelligence Dashboard]
    end
    
    subgraph API_Layer [Backend - FastAPI]
        Result -->|POST /api/analyze| Analyze[Analysis Endpoint]
        Analyze -->|Scrape| SCR[BS4 Scraper]
        SCR -->|Analyze| LLM[Groq AI Engine]
        LLM -->|Validate| PYD[Pydantic Models]
    end
    
    subgraph Output_Layer [Visual Intelligence]
        PYD -->|D3.js| Graph[Narrative Network]
        PYD -->|Recharts| Charts[Bias Metrics]
        PYD -->|Synthesis| Report[Comparative Report]
    end
```

---

## Getting Started

### Prerequisites
*   Python 3.12+
*   **uv** (Fast Python package manager)
*   Node.js 22+ & npm
*   Groq Cloud API Key

### 1. Backend Setup
```bash
cd backend

# Install dependencies using uv
uv sync

# Create .env file
echo "GROQ_API_KEY=your_key_here" > .env

# Run the server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Setup
```bash
cd frontend
# Install dependencies
npm install
# Start development server
npm run dev
```

The application will be available at `http://localhost:5173`.

---

## Methodology

Omnius implements the **Robert Entman's Framing Theory (1993)**, which identifies:
1. **Problem Definition**: What is the core issue at hand?
2. **Causal Interpretation**: Who or what is blamed for the problem?
3. **Moral Evaluation**: How are the actors and actions judged?
4. **Treatment Recommendation**: What is the suggested solution or path forward?

By comparing these pillars across sources, Omnius reveals the systematic "framing" that shapes public perception.

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## Author

**Felix Hardyan**
*   [GitHub](https://github.com/flxhrdyn)
*   [Hugging Face](https://huggingface.co/felixhrdyn)

---
<div align="center">
  Built for Objective Media Analysis.
</div>
