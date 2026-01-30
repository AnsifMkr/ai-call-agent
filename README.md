# AI Call Agent Resilience System

A robust, dependency-free error recovery system designed to handle third-party service failures (like ElevenLabs outages) gracefully.

## 🏗 Architecture

### 1. Custom Exception Hierarchy
- `BaseResilienceError`: Root of all custom errors.
- `TransientError`: Temporary failures (503, Timeout) -> **Triggers Retry**.
- `PermanentError`: Non-recoverable (401, 400) -> **Fast Fail**.
- `CircuitBreakerOpenError`: Raised when a service is unhealthy.

### 2. Resilience Primitives (No External Libraries)
- **RetryManager**: Implements exponential backoff (Initial: 1s, Factor: 2x).
- **CircuitBreaker**: 
  - Tracks failure counts.
  - States: `CLOSED` -> `OPEN` (after 3 failures) -> `HALF_OPEN` (after 15s timeout).
  - Prevents cascading failures by blocking calls to unhealthy services.

### 3. Observability
- **Structured Logs**: JSON logs saved to `system_logs.json`.
- **Google Sheets Integration**: Simulates appending rows to `mock_google_sheets.csv`.
- **Alerting**: Multi-channel alerts (Email, Telegram, Webhook) triggered on critical failures (CB Open).

## 🚀 Usage

### Prerequisites
- Python 3.x
- No external `pip install` required for core logic (standard library only).

### Running the Simulation
Execute the main script to run the **ElevenLabs 503 Outage Scenario**:

```bash
python3 main.py
```

### Scenario Walkthrough
1. **User_A**: System is healthy. Call succeeds.
2. **Injection**: `ElevenLabsService.simulate_503` is set to `True`.
3. **User_B**:
   - Encounter 503 Error.
   - **Retry 1**: Wait 1s.
   - **Retry 2**: Wait 2s.
   - **Retry 3**: Wait 4s.
   - **Fail**: Alert triggered ("Circuit Breaker OPEN").
4. **User_C**: Circuit Breaker is **OPEN**. Call is skipped immediately (Fail Fast).
5. **Recovery**: `ElevenLabsService.simulate_503` is set to `False`.
6. **User_E/F**: After 15s, Circuit Breaker enters **HALF_OPEN**.
   - A probe request is allowed.
   - Success -> Circuit Breaker resets to **CLOSED**.
   - Normal processing resumes.

## 📂 Project Structure
```
.
├── main.py                     # Entry point & Simulation
├── src
│   ├── core
│   │   ├── exceptions.py       # Custom Exception Hierarchy
│   │   └── resilience.py       # Retry & Circuit Breaker Logic
│   ├── observability
│   │   ├── alerter.py          # Alerting Channels
│   │   └── logger.py           # File & Sheets Logging
│   └── services
│       ├── base_service.py     # Base wrapper with Resilience
│       ├── elevenlabs_service.py
│       └── llm_service.py
├── system_logs.json            # Generated Logs
└── mock_google_sheets.csv      # Generated Sheet Data
```
