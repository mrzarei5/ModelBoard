# ModelBoard: Agentic RAG for LLM Leaderboard Discovery

A modular conversational app for searching, filtering, and comparing top open-source large language models, powered by agentic RAG (retrieval-augmented generation) and a curated leaderboard database.

---

*Interactive semantic search and model comparison, powered by agentic RAG.*
![App Screenshot](assets/app.png)  

---

## 🚀 Features

* **Conversational agentic interface** for model discovery, search, and comparison.
* **Semantic search** across curated leaderboard models (Open LLM Leaderboard, Hugging Face).
* **Advanced filtering** by task, tags, provider, license, benchmark score, parameter count, etc.
* **Model comparison** with detailed metadata, benchmark, and license info.
* **Tool-using agent** architecture (LangChain) with modular, extensible codebase.
* **Local, fast, and reproducible**: all model data indexed and embedded locally—no need to hit Hugging Face API at query time.
* **Streamlit web UI**—easy to run, easy to extend.

---

## 🛠️ Getting Started

### Option 1: Local Python/Conda Installation

1. **Clone and install**

```bash
git clone https://github.com/mrzarei5/ModelBoard.git
cd modelboard-agentic-rag

# Create and activate a conda environment
conda create -n modelboard python=3.10
conda activate modelboard

# Install requirements
pip install -r requirements.txt
```

2. **Set your API keys**

Create a `.env` file in the project root directory and add your OpenAI API key:

```ini
OPENAI_API_KEY=sk-...
```
(Optional) Add your Hugging Face API key:
```ini
HF_API_KEY=hf-...
```

3. **(Optional) Update model leaderboard metadata**

To download or refresh the leaderboard data:
```bash
python data/fetch_leaderboard.py
```
This will (re)generate `model_metadata.json` in the `data` folder.

4. **Run the app**

```bash
streamlit run main.py
```

---

### Option 2: Run with Docker

1. **Clone the repository**

```bash
git clone https://github.com/mrzarei5/ModelBoard.git
cd ModelBoard
```

2. **Create a `.env` file**

In the project root, create a file named `.env` with your API keys:
```ini
OPENAI_API_KEY=sk-...
# (Optional) Hugging Face API key:
# HF_API_KEY=hf-...
```

3. **Build the Docker image**

```bash
docker build -t modelboard .
```

4. **(Optional) Update model leaderboard metadata inside the container**

```bash
docker run --rm -v $(pwd)/data:/app/data modelboard python data/fetch_leaderboard.py
```

5. **Run the app**

```bash
docker run -p 8501:8501 -v $(pwd)/data:/app/data modelboard
```

- The app will be available at: [http://localhost:8501](http://localhost:8501)
- For persistent leaderboard data, mount the `data/` directory as shown above.

---

## 🗂️ Example Queries

* *Show all chat models with Apache-2.0 license.*
* *Find a multilingual model for question answering.*
* *Compare meta-llama/Llama-2-70b-chat-hf and mistralai/Mistral-7B-Instruct-v0.3.*
* *Give me details about openchat/openchat-3.5-0106.*

---

## 📝 License

This project is licensed under the Apache License, Version 2.0.  
See the [LICENSE](LICENSE) file for details.

---

## 🤝 Acknowledgements

* [Hugging Face Open LLM Leaderboard](https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard)
* [LangChain](https://github.com/langchain-ai/langchain)
* [ChromaDB](https://www.trychroma.com/)
* [SentenceTransformers](https://www.sbert.net/)
* [Streamlit](https://streamlit.io/)
