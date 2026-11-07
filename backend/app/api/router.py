from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.auth_check import router as auth_check_router
from app.api.profiles import router as profiles_router
from app.api.skills import router as skills_router
from app.api.cv import router as cv_router
from app.api.evaluation import router as evaluation_router
from app.api.jobs import router as jobs_router
from app.api.matching import router as matching_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(auth_check_router)
api_router.include_router(profiles_router)
api_router.include_router(skills_router)
api_router.include_router(cv_router)
api_router.include_router(evaluation_router)
api_router.include_router(jobs_router)
api_router.include_router(matching_router)
