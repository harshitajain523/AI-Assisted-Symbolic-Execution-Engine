## Backend Setup

1. Ensure LLVM/Clang 14, KLEE, and Z3 are installed on your system and their binaries are accessible.
2. Create a virtual environment and install Python dependencies:

   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Export the Gemini API key so the repair endpoint can reach the model:

   ```bash
   export GEMINI_API_KEY=your_key_here
   ```

4. Launch the FastAPI application (uvicorn installed in the venv):

   ```bash
   uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
   ```

## Frontend Setup

1. Install Node 18+.
2. From the repository root run:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   The dashboard defaults to `http://localhost:5173` and proxies API calls to `http://localhost:8000`. Override the backend URL by setting `VITE_API_BASE_URL` before running `npm run dev`.

## End-to-End Test

With both servers running, open the dashboard, keep the default sample program, and click **Run Full Analysis**. Once results appear, trigger **Run AI Repair**, **Build Final Report**, and **Export HTML** to execute every FR1–FR13 feature path described in the SRS.

