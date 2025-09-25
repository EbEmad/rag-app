# mini-rag
how to build a production-ready app for RAG application.


#  Project Setup with Docker

This project uses **Docker** to run a Jupyter Notebook environment.

---

##  Requirements
Before you begin, make sure you have the following installed:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

---

##  Getting Started

Follow these steps to run the project inside Docker:

### Clone the Repository
```bash
git clone https://github.com/EbEmad/mini-rag.git
cd mini-rag

### Setup the environment variables

```bash
$ cp .env.example .env
```

Set your environment variables in the `.env` file. Like `OPENAI_API_KEY` value.

## Run the FastAPI server

```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```