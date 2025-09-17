from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from database.models import User, get_db, create_tables
from auth.auth import authenticate_user, create_access_token, get_password_hash, get_current_user, verify_token
from schemas.schemas import UserCreate, UserLogin, UserResponse, Token, UserUpdate
import os
from dotenv import load_dotenv

load_dotenv()

# Tables will be created by the main app

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Token expiration time
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Display registration page"""
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    name: str = Form(...),
    surname: str = Form(...),
    email: str = Form(...),
    company_name: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "Email already registered. Please use a different email or try logging in."
            })
        
        # Create new user
        hashed_password = get_password_hash(password)
        new_user = User(
            name=name,
            surname=surname,
            email=email,
            company_name=company_name,
            hashed_password=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Redirect to login page with success message
        return RedirectResponse(url="/login?message=Registration successful! Please log in.", status_code=303)
        
    except Exception as e:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": f"Registration failed: {str(e)}"
        })

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, message: str = None):
    """Display login page"""
    return templates.TemplateResponse("login.html", {
        "request": request,
        "message": message
    })

@router.post("/login", response_class=HTMLResponse)
async def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Authenticate user and create session"""
    try:
        # Authenticate user
        user = authenticate_user(db, email, password)
        if not user:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Invalid email or password"
            })
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        # Redirect to main page with token in session
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        return response
        
    except Exception as e:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": f"Login failed: {str(e)}"
        })

@router.get("/logout")
async def logout():
    """Logout user and clear session"""
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="access_token")
    return response

def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    """Get current user from cookie token"""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                return user
    except:
        pass
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated"
    )

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, current_user: User = Depends(get_current_user_from_cookie), message: str = None):
    """Display user profile page"""
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": current_user,
        "message": message
    })

@router.get("/api/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information via API"""
    return current_user

@router.get("/profile/edit", response_class=HTMLResponse)
async def profile_edit_page(request: Request, current_user: User = Depends(get_current_user_from_cookie)):
    """Display profile edit page"""
    return templates.TemplateResponse("profile_edit.html", {
        "request": request,
        "user": current_user
    })

@router.post("/profile/update", response_class=HTMLResponse)
async def update_profile(
    request: Request,
    name: str = Form(...),
    surname: str = Form(...),
    email: str = Form(...),
    company_name: str = Form(...),
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    try:
        # Check if email is being changed and if it's already taken
        if email != current_user.email:
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                return templates.TemplateResponse("profile_edit.html", {
                    "request": request,
                    "user": current_user,
                    "error": "Email already taken by another user. Please choose a different email."
                })
        
        # Update user data
        current_user.name = name
        current_user.surname = surname
        current_user.email = email
        current_user.company_name = company_name
        current_user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(current_user)
        
        # Redirect to profile page with success message
        response = RedirectResponse(url="/profile?message=Profile%20updated%20successfully!", status_code=303)
        return response
        
    except Exception as e:
        return templates.TemplateResponse("profile_edit.html", {
            "request": request,
            "user": current_user,
            "error": f"Update failed: {str(e)}"
        })
