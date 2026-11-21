from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import DB_PATH
from app.database import init_db, init_extra_tables
from app.routers import career, portfolio, readiness, twin, intake, jobs, plan, interview, applications


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database schema
    init_db(DB_PATH)
    init_extra_tables(DB_PATH)
    yield


app = FastAPI(
    title="CareerPilot AI Backend",
    version="1.0.0",
    description="CareerPilot AI — Career Twin, Readiness Scoring, Simulator & Portfolio Generator",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Standardized error response handler for consistent JSON shape
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    error_code = "NOT_FOUND" if exc.status_code == 404 else "BAD_REQUEST"
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": error_code},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal server error: {str(exc)}", "error_code": "INTERNAL_ERROR"},
    )


# Register Feature Routers
app.include_router(readiness.router)
app.include_router(career.router)
app.include_router(twin.router)
app.include_router(portfolio.router)
app.include_router(intake.router)
app.include_router(jobs.router)
app.include_router(plan.router)
app.include_router(interview.router)
app.include_router(applications.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "CareerPilot AI Backend"}
