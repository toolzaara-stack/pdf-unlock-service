🚀 ToolZaara PDF Unlock & Repair Microservice
A lightning-fast, high-performance backend microservice built with Python + FastAPI, powered by PyMuPDF (fitz) and multi-threaded dictionary-attack capabilities to decrypt, bypass PDF restrictions, and repair corrupted structures seamlessly.

📁 Project Structure:
main.py: The complete API application featuring CORS support, auto-decryption multi-threading, and streaming/file responses.

requirements.txt: Required Python dependencies.

Dockerfile: Configuration for building a lightweight and fast Docker container.

docker-compose.yml: For deploying and running the service with a single command on any VPS.

🛠️ Deployment & Execution Options:
1️⃣ Local or Server Execution (Direct Python):
Bash
pip install -r requirements.txt
python main.py
The API will run locally at: http://localhost:8000

2️⃣ Running via Docker (on any VPS like Hostinger VPS):
Bash
docker compose up -d --build
3️⃣ Free Cloud Hosting on Render.com / Railway:
Push the repository files to your GitHub account.

Log in to Render.com and click New Web Service.

Select your repository, and Render will automatically detect the Dockerfile, build it instantly, and provide a free HTTPS URL (e.g., [https://toolzaara-pdf.onrender.com](https://toolzaara-pdf.onrender.com)).

🔗 Endpoints:
GET /: Health check to verify service status.

POST /api/unlock-pdf:

file: The target PDF file (Multipart/form-data).

password: Optional manual password parameter (though the service automatically tests thousands of common passwords in the background if omitted).
