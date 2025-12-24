# app/routers/upload.py

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from typing import List
import os
import uuid
from pathlib import Path
import shutil
import imghdr
from app.middleware.auth import security

router = APIRouter()

# Configuration
UPLOAD_DIR = Path("uploads/books")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
MIN_FILE_SIZE = 1024  # 1 KB
MAX_FILES_PER_UPLOAD = 5

# Create upload directory
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def validate_image_file(file: UploadFile) -> None:
    """
    Comprehensive image validation
    
    Checks:
    - File extension
    - MIME type
    - Actual image format (using imghdr)
    - File size
    """
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extension non autorisée. Extensions acceptées: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Type de fichier non autorisé. Types acceptés: {', '.join(ALLOWED_MIME_TYPES)}"
        )
    
    # Check file size
    file.file.seek(0, 2)  # Go to end
    file_size = file.file.tell()
    file.file.seek(0)  # Back to start
    
    if file_size < MIN_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fichier trop petit (minimum 1 KB)"
        )
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fichier trop volumineux. Taille maximum: {MAX_FILE_SIZE / (1024*1024):.1f} MB"
        )
    
    # Verify actual image format
    file.file.seek(0)
    header = file.file.read(512)
    file.file.seek(0)
    
    image_type = imghdr.what(None, header)
    if image_type not in ['jpeg', 'png', 'webp', 'gif']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier n'est pas une image valide"
        )

def sanitize_filename(filename: str) -> str:
    """Remove potentially dangerous characters from filename"""
    # Keep only alphanumeric, dots, hyphens, underscores
    import re
    safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    return safe_name

@router.post("/upload", response_model=dict)
async def upload_book_image(
    file: UploadFile = File(...),
    token: str = Depends(security)
):
    """
    Upload a single book image (PROTECTED ROUTE)
    
    - **file**: Image file (JPG, PNG, WEBP, GIF)
    - Maximum size: 5 MB
    - Minimum size: 1 KB
    - Returns the URL of the uploaded image
    
    Security features:
    - File type validation
    - Size limits
    - Format verification
    - Unique filename generation
    """
    try:
        # Validate image
        validate_image_file(file)
        
        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1].lower()
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size for response
        file_size = os.path.getsize(file_path)
        
        # Return relative URL
        file_url = f"/uploads/books/{unique_filename}"
        
        print(f"✅ Image uploaded: {unique_filename} ({file_size} bytes)")
        
        return {
            "message": "Image uploadée avec succès",
            "filename": unique_filename,
            "url": file_url,
            "size": file_size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'upload: {str(e)}"
        )

@router.post("/upload-multiple", response_model=dict)
async def upload_multiple_images(
    files: List[UploadFile] = File(...),
    token: str = Depends(security)
):
    """
    Upload multiple book images (maximum 5 images)
    
    - **files**: List of image files
    - Maximum 5 images per request
    - Each image: maximum 5 MB
    - Returns URLs of all uploaded images
    """
    if len(files) > MAX_FILES_PER_UPLOAD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {MAX_FILES_PER_UPLOAD} images par requête"
        )
    
    uploaded_files = []
    errors = []
    
    for file in files:
        try:
            # Validate file
            validate_image_file(file)
            
            # Generate unique filename
            file_ext = os.path.splitext(file.filename)[1].lower()
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = UPLOAD_DIR / unique_filename
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            file_size = os.path.getsize(file_path)
            
            uploaded_files.append({
                "original_filename": file.filename,
                "filename": unique_filename,
                "url": f"/uploads/books/{unique_filename}",
                "size": file_size
            })
            
            print(f"✅ Image uploaded: {unique_filename}")
            
        except HTTPException as e:
            errors.append({
                "filename": file.filename,
                "error": e.detail
            })
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "message": f"{len(uploaded_files)} image(s) uploadée(s)",
        "uploaded": uploaded_files,
        "errors": errors if errors else None,
        "total_uploaded": len(uploaded_files),
        "total_failed": len(errors)
    }

@router.delete("/delete/{filename}")
async def delete_image(
    filename: str,
    token: str = Depends(security)
):
    """
    Delete an uploaded image (PROTECTED ROUTE)
    
    - **filename**: Name of the file to delete
    - Only the uploader can delete their images (implement user check if needed)
    """
    try:
        # Sanitize filename to prevent directory traversal
        safe_filename = sanitize_filename(filename)
        file_path = UPLOAD_DIR / safe_filename
        
        # Check if file exists
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image non trouvée"
            )
        
        # Verify it's actually in the uploads directory (security check)
        if not str(file_path.resolve()).startswith(str(UPLOAD_DIR.resolve())):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès refusé"
            )
        
        # Delete file
        os.remove(file_path)
        
        print(f"🗑️ Image deleted: {safe_filename}")
        
        return {
            "message": "Image supprimée avec succès",
            "filename": safe_filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Delete error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )

@router.get("/test")
def test_upload():
    """Test endpoint"""
    return {
        "message": "Upload router is working!",
        "config": {
            "max_file_size_mb": MAX_FILE_SIZE / (1024*1024),
            "allowed_extensions": list(ALLOWED_EXTENSIONS),
            "max_files_per_upload": MAX_FILES_PER_UPLOAD
        }
    }
