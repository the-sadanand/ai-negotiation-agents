# 🤖 AI Negotiation Agents

> A multi-agent AI system where two autonomous LLM-powered negotiators (🇺🇸 USA and 🇨🇳 China) simulate trade agreement negotiations over multiple rounds using **Ollama**, **Llama 3**, and **FastAPI**.

---

## 📖 Overview

AI Negotiation Agents demonstrates how multiple Large Language Model (LLM) agents can negotiate with one another while representing different national interests.

Each agent is assigned its own negotiation objectives, priorities, and flexibility levels. During every negotiation round, the agents exchange proposals, evaluate compromises, and work toward a mutually acceptable trade agreement.

This project is designed to showcase:

- 🤖 Multi-Agent AI Systems
- 🧠 LLM-based Decision Making
- 💬 Autonomous Negotiation
- ⚡ FastAPI Backend
- 🐳 Dockerized Deployment
- 🧪 Automated Testing with Pytest

---

## 🚀 Features

- 🇺🇸 USA AI Negotiator
- 🇨🇳 China AI Negotiator
- 🔄 Multi-round negotiation process
- 📊 Compromise scoring system
- 📁 Configurable country priorities via JSON
- ⚡ REST API using FastAPI
- 🐳 Docker & Docker Compose support
- 🧪 Pytest test suite
- 🖥️ Local LLM inference using Ollama + Llama 3

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.11 | Core Programming Language |
| FastAPI | REST API Framework |
| Ollama | Local LLM Runtime |
| Llama 3 | AI Negotiation Model |
| Docker | Containerization |
| Docker Compose | Multi-service Orchestration |
| Pytest | Automated Testing |

---

## 📂 Project Structure

```text
AI-Negotiation-Agents/
│
├── agents/
│   └── negotiator.py          # AI negotiator agent
│
├── data/
│   └── trade_positions.json   # Country priorities & flexibility
│
├── tests/
│   └── test_negotiation.py    # Pytest test suite
│
├── main.py                    # FastAPI application
├── scoring.py                 # Compromise scoring logic
├── Dockerfile                 # API container
├── docker-compose.yml         # Multi-container setup
└── README.md
```

---

# ⚙️ Installation

## Clone the Repository

```bash
git clone https://github.com/your-username/AI-Negotiation-Agents.git

cd AI-Negotiation-Agents
```

---

## Start the Services

```bash
docker-compose up --build -d
```

---

## Download the Llama 3 Model

```bash
docker-compose exec ollama ollama pull llama3
```

---

## Run the API

The FastAPI server will be available at:

```
http://localhost:8000
```

Swagger Documentation:

```
http://localhost:8000/docs
```

---

# 📡 API

## Start a Negotiation

**Endpoint**

```http
POST /negotiate
```

### Request Body

```json
{
    "issue": "Technology Tariffs",
    "rounds": 3
}
```

### Example Request

```bash
curl -X POST http://localhost:8000/negotiate \
-H "Content-Type: application/json" \
-d '{
      "issue":"Technology Tariffs",
      "rounds":3
    }'
```

### Example Response

```json
{
  "issue": "Technology Tariffs",
  "rounds": 3,
  "agreement": true,
  "score": 82,
  "summary": "Both countries agreed to reduce tariffs while protecting strategic industries."
}
```

---

# 🧠 How It Works

1. User submits a negotiation topic.
2. USA agent generates its proposal.
3. China agent responds with a counterproposal.
4. Both agents negotiate over multiple rounds.
5. A scoring system evaluates the level of compromise.
6. Final agreement and negotiation summary are returned.

---

# 🧪 Running Tests

Execute the test suite:

```bash
pytest
```

or

```bash
pytest -v
```

---

# 🐳 Docker Commands

Build and start containers:

```bash
docker-compose up --build -d
```

Stop containers:

```bash
docker-compose down
```

View logs:

```bash
docker-compose logs -f
```

Restart services:

```bash
docker-compose restart
```

---

# 📈 Future Improvements

- 🌍 Support additional countries
- 🧠 Memory across negotiation rounds
- 📊 Negotiation analytics dashboard
- 🎯 Reinforcement Learning for strategy optimization
- 📄 Negotiation transcript export
- 🔐 Authentication & rate limiting
- 🌐 Web-based frontend

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a new feature branch

```bash
git checkout -b feature/new-feature
```

3. Commit your changes

```bash
git commit -m "Add new feature"
```

4. Push to your branch

```bash
git push origin feature/new-feature
```

5. Open a Pull Request

---

# 📄 License

This project is licensed under the MIT License.

---

# ⭐ Show Your Support

If you found this project helpful, consider giving it a ⭐ on GitHub. It helps others discover the project and supports future improvements.