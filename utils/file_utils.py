import os
from typing import Optional
from fastapi import UploadFile, HTTPException

class FileUtils:
    ALLOWED_EXTENSIONS = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "doc": "application/msword",
        "eml": "message/rfc822",
        "email": "message/rfc822"
    }
    
    @staticmethod
    def validate_file(file: UploadFile) -> str:
        """Validate uploaded file and return file type"""
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        # Check file extension
        file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        
        if file_extension not in FileUtils.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed types: {', '.join(FileUtils.ALLOWED_EXTENSIONS.keys())}"
            )
        
        # Check file size (max 10MB)
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")
        
        return file_extension
    
    @staticmethod
    async def read_file_content(file: UploadFile) -> bytes:
        """Read file content as bytes"""
        try:
            content = await file.read()
            return content
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
    
    @staticmethod
    def get_file_type_from_extension(extension: str) -> str:
        """Get standardized file type from extension"""
        extension_map = {
            "pdf": "pdf",
            "docx": "docx",
            "doc": "docx",
            "eml": "email",
            "email": "email"
        }
        return extension_map.get(extension.lower(), "unknown")
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove or replace unsafe characters
        unsafe_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        for char in unsafe_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 100:
            name, ext = os.path.splitext(filename)
            filename = name[:100-len(ext)] + ext
        
        return filename 