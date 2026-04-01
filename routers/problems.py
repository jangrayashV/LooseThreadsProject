from fastapi import APIRouter, Depends, HTTPException
from db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from routers.users import get_current_user
from schemas.schemas import ProblemCreate, ProblemResponse, HintResponse, ProblemWithHints
from services.llm import get_hint
from models.models import Problems, User, Hints
from sqlalchemy import select

router = APIRouter(prefix="/problems", tags=["problems"])

@router.post("/create", response_model=ProblemResponse)
async def create_problem(problem: ProblemCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_problem = Problems(
        uid=current_user.uid,
        title=problem.title,
        description=problem.description,
        attempted_approach=problem.attempted_approach
    )
    db.add(new_problem)
    await db.commit()
    await db.refresh(new_problem)
    return new_problem

@router.post("/{pid}/hint", response_model=HintResponse)
async def get_problem_hint(pid: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    response = await db.execute(select(Problems).where(Problems.pid == pid , Problems.uid == current_user.uid))
    existing_problem = response.scalar_one_or_none()
    if not existing_problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    response = await db.execute(select(Hints).where(Hints.pid == pid))
    existing_hints = response.scalars().all()
    if len(existing_hints) >= 3:
        raise HTTPException(status_code=400, detail="Maximum hints reached for this problem")  
    hint_number = len(existing_hints) + 1
    
    hint_content = await get_hint(existing_problem.title, existing_problem.description, existing_problem.attempted_approach, hint_number)

    new_hint = Hints(
        pid=pid,
        hint_count=hint_number,
        content=hint_content["hint"]
    )

    if not existing_problem.type:
        existing_problem.type = hint_content["pattern"]

    db.add(new_hint)
    await db.commit()
    await db.refresh(new_hint)
    return new_hint

@router.get("/", response_model=list[ProblemResponse])
async def get_user_problems(page: int = 1, limit: int = 10,db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    offset = (page - 1) * limit
    response = await db.execute(select(Problems).where(Problems.uid == current_user.uid).offset(offset).limit(limit))
    existing_problems = response.scalars().all()
    return existing_problems

@router.get("/{pid}/hints", response_model=list[HintResponse])
async def get_problem_hints(pid: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Hints).where(Hints.pid == pid).order_by(Hints.hint_count))
    return result.scalars().all()

@router.get("/{pid}", response_model=ProblemWithHints)
async def get_problem(pid: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    response = await db.execute(select(Problems).where(Problems.pid == pid, Problems.uid == current_user.uid))
    existing_problem = response.scalar_one_or_none()

    response = await db.execute(select(Hints).where(Hints.pid == pid))
    existing_hints = response.scalars().all()

    if not existing_problem:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    data = ProblemWithHints(
        problem=existing_problem,
        hints=existing_hints
    )
    return data

@router.delete("/{pid}")
async def delete_problem(pid: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    response = await db.execute(select(Problems).where(Problems.pid == pid, Problems.uid == current_user.uid))
    existing_problem = response.scalar_one_or_none()
    if not existing_problem:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    await db.delete(existing_problem)
    await db.commit()
    return {"detail": "Problem deleted successfully"}