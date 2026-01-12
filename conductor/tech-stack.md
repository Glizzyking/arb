# Technology Stack

## Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.9+ | Core runtime |
| FastAPI | 0.100+ | REST API framework |
| Uvicorn | 0.20+ | ASGI server |
| Requests | 2.31+ | HTTP client for external APIs |
| Pytz | 2023+ | Timezone handling |
| Websockets | Latest | Backend WebSocket server streaming |
| Pytest | 7.x | Testing framework (for tracker validation) |

### Backend Modules
- **`backend/tracker/`**: New modular tracker system handling time-based URL generation and multi-crypto API clients.


## Frontend
| Technology | Version | Purpose |
|-----------|---------|---------|
| Next.js | 16.0.4 | React framework with App Router |
| React | 19.2.0 | UI library |
| TypeScript | 5.x | Type-safe JavaScript |
| Tailwind CSS | 4.x | Utility-first CSS |
| shadcn/ui | Latest | UI component library (Radix-based) |
| Lucide React | 0.555+ | Icons |

## External APIs
| API | Purpose |
|-----|---------|
| Polymarket Gamma API | Event metadata |
| Polymarket CLOB API | Order book prices |
| Kalshi Trade API | Market prices |

## Development Tools
| Tool | Purpose |
|------|---------|
| ESLint | Code linting |
| Git | Version control |
