# Mini RAG App
### Implementation of a mini RAG system for Question Answering.

---


## Installation

### 1. Install Python
Download and install **Miniconda** from the [official website](https://www.anaconda.com/docs/getting-started/miniconda/main#quick-command-line-install).

---

### 2. Create a new environment
```bash
conda create -n mini-rag python=3.10
```

### 3. Activate the environment
```bash
conda activate mini-rag
```

### 4. Install the required packages
```bash
pip install -r requirements.txt
```


### 5. Setup the environment variables
```bash
cp .env.example .env
```

## Run Docker Compose Services
```bash
cd docker
cp .env.example .env
```

```bash
cd docker
sudo docker compose up -d
```


## Run the FastAPI server
```bash
uvicorn main:app --reload --port 5000
```