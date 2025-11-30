
# AI-Assisted Symbolic Execution Engine

A full-stack application that combines KLEE symbolic execution with AI-powered code repair capabilities. The system analyzes C programs for memory safety vulnerabilities, generates repair suggestions using Google's Gemini API, and validates the fixes through automated testing.

## Features

- **Symbolic Execution Analysis**: Uses KLEE to explore program paths and detect bugs
- **AI-Powered Repair**: Leverages Gemini 2.5 Flash to generate code fixes
- **Automated Validation**: Re-runs KLEE on repaired code to verify fixes
- **Comprehensive Reporting**: Generates detailed HTML reports with analysis results
- **Interactive Dashboard**: Modern React-based UI for code input and results visualization

## System Requirements

### Backend Dependencies
- **LLVM/Clang 14+**: For compiling C code to LLVM bitcode
- **KLEE**: Symbolic execution engine
- **Z3 Solver**: Used by KLEE for constraint solving
- **Python 3.8+**: Backend runtime
- **Google Gemini API Key**: For AI repair functionality

### Frontend Dependencies
- **Node.js 18+**: Frontend runtime
- **npm**: Package manager

## Installation

### 1. Clone the Repository

```bash
git clone <your-github-repo-url>
cd swe_project
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Set Up Gemini API Key

You need a Google Gemini API key for the AI repair feature:

1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Export it as an environment variable:

```bash
# On Linux/macOS:
export GEMINI_API_KEY=your_key_here

# On Windows (PowerShell):
$env:GEMINI_API_KEY="your_key_here"

# On Windows (CMD):
set GEMINI_API_KEY=your_key_here
```

**Note**: You'll need to set this environment variable every time you start a new terminal session, or add it to your shell profile (`.bashrc`, `.zshrc`, etc.) to make it persistent.

### 4. Frontend Setup

```bash
cd frontend

# Install Node.js dependencies
npm install
```

## Running the Application

### Start the Backend Server

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`

### Start the Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend dashboard will be available at `http://localhost:5173`

**Note**: Make sure the backend is running before using the frontend, as the frontend makes API calls to the backend.

## Usage

1. **Open the Dashboard**: Navigate to `http://localhost:5173` in your browser
2. **Input C Code**: Use the default sample code or paste your own C program (must include `klee_make_symbolic` calls for symbolic variables)
3. **Run Full Analysis**: Click "Run Full Analysis" to compile and analyze your code with KLEE
4. **AI Repair**: After analysis, click "Run AI Repair" to get AI-generated fixes for detected bugs
5. **Build Report**: Generate a consolidated report combining analysis and repair results
6. **Export HTML**: Export a comprehensive HTML report to the workspace

## Project Structure

```
swe_project/
├── backend/
│   ├── src/
│   │   ├── ai/
│   │   │   └── repair_module.py      # AI repair generation
│   │   ├── api/
│   │   │   └── app.py                # FastAPI application
│   │   ├── compiler/
│   │   │   └── bitcode.py            # C to LLVM compilation
│   │   ├── executor/
│   │   │   ├── klee_runner.py        # KLEE execution
│   │   │   ├── coverage_analyzer.py  # Code coverage analysis
│   │   │   └── ktest_parser.py       # Test case parsing
│   │   └── reporting/
│   │       └── html_generator.py     # HTML report generation
│   ├── requirements.txt              # Python dependencies
│   └── README.md                      # Backend-specific docs
├── frontend/
│   ├── src/
│   │   ├── components/               # React components
│   │   ├── api.ts                    # API client
│   │   ├── App.tsx                   # Main application
│   │   └── types.ts                  # TypeScript types
│   ├── package.json                  # Node.js dependencies
│   └── vite.config.ts                # Vite configuration
├── .gitignore
└── README.md                          # This file
```

## API Endpoints

- `POST /full-analysis`: Compile and analyze C code
- `POST /repair`: Generate AI repair suggestions and validate them
- `POST /report`: Build consolidated final report
- `POST /generate-report`: Generate HTML report
- `GET /health`: Health check endpoint

## Troubleshooting

### AI Repair Not Working

If you see "GEMINI_API_KEY environment variable is missing":
- Make sure you've exported the API key in the terminal where you're running the backend
- Restart the backend server after setting the environment variable
- Verify the key is valid by checking [Google AI Studio](https://makersuite.google.com/app/apikey)

### KLEE Not Found

- Ensure KLEE is installed and accessible in your PATH
- Verify installation: `klee --version`
- Check that LLVM/Clang 14+ is installed: `clang --version`

### Frontend Can't Connect to Backend

- Ensure the backend is running on port 8000
- Check that CORS is enabled (it should be by default)
- Verify `VITE_API_BASE_URL` if you've customized the backend URL

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Authors

- **Harshita Jain** (23UCC547)
