Got it! You want a **clean README file** that explains your project structure, how to clone it, run it, and set up Docker for Ollama **without showing any `__pycache__` files**. Here's a structured example for your README:

---

# Formation LLM

This project demonstrates working with LLM services, including Ollama, in Python and Docker.

## Project Structure

```
├── app
│   ├── api
│   │   ├── routes_health.py       # Defines API routes for health checks and server status
│   │   └── routes_llm.py          # Defines API routes to interact with the LLM service
│   ├── chroma_db
│   │   ├── 13f47807-986c-4620-b83a-e1c7f5f6ec35
│   │   │   ├── data_level0.bin   # Chroma DB vector data
│   │   │   ├── header.bin        # Chroma DB header file
│   │   │   ├── length.bin        # Chroma DB length metadata
│   │   │   └── link_lists.bin    # Chroma DB link lists for vectors
│   │   └── chroma.sqlite3        # SQLite database for Chroma
│   ├── core
│   │   └── config.py             # Configuration settings (paths, keys, environment variables)
│   ├── logs
│   │   └── app.log               # Application log file
│   ├── main.py                   # Entry point of the FastAPI application
│   ├── schemas
│   │   └── llm_schema.py         # Pydantic models for LLM request/response validation
│   ├── services
│   │   ├── document
│   │   │   └── ISITCOM_MARS_Lab_Report.pdf   # Example document used for processing/search
│   │   ├── llm_router.py         # Functions to route requests to the LLM service
│   │   ├── nvidia_services.py    # Handles Nvidia GPU-related services (if any)
│   │   ├── ollama_service.py     # Service functions to interact with Ollama LLM
│   │   ├── rag_services.py       # RAG (Retrieval-Augmented Generation) service functions
│   │   └── students.txt          # Sample or test data file for students
│   ├── tools
│   │   └── StudentTool.py        # Utility functions related to student data processing
│   └── utils
│       └── logger.py             # Custom logger setup for the application
├── docker
│   ├── docker-compose.yml        # Docker Compose configuration for running app + services
│   └── Dockerfile                # Dockerfile to build the app image
├── README.md                     # Project documentation
└── requirements.txt              # Python dependencies

```

> **Note:** `__pycache__` folders are excluded from this view.

---

## Getting Started

### Clone the Repository

```bash
git clone https://github.com/abdelkarimse/formation_llm.git
cd formation_llm
```

### Install Python Dependencies

It's recommended to use a virtual environment:

```bash
python -m venv myenv
source myenv/bin/activate   # Linux / Mac
myenv\Scripts\activate      # Windows

pip install -r requirements.txt
```

### Run the Python App

```bash
cd app
python main.py
```

This will start the FastAPI application. You can access the API endpoints:

* Health check: `http://localhost:8000/api/health`
* LLM endpoints: `http://localhost:8000/api/llm`

---

## Running Ollama with Docker

1. Make sure Docker is installed: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
2. Navigate to the `docker` folder:

```bash
cd docker
docker-compose up -d
ollama run qwen3:4b --keep_alive=-1   
```

This will start Ollama and your app in Docker containers.



Repository of Llm 2x faster with 70% less VRAM! [here](https://github.com/unslothai/unsloth?tab=readme-ov-file):