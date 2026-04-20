from fastapi import UploadFile, HTTPException, status
from app.core.supabase import supabase, SUPABASE_BUCKET
import uuid
from uuid import UUID
from app.enums.storage_folder import StorageFolderEnum

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp", "bmp", "svg"}

#FUNCION PARA GUARDAR LAS IMAGENES EN EL BUCKET DE SUPABASE
def sv_upload_file(file: UploadFile, folder: StorageFolderEnum, user_id : UUID ) -> str:
    try:
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type '.{file_ext}'. Allowed formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )
        original_name = file.filename.rsplit(".", 1)[0]
        file_name = f"{folder.value}/{user_id}/{original_name}.{file_ext}"
        content = file.file.read()

        supabase.storage.from_(SUPABASE_BUCKET).upload(
            path=file_name,
            file = content,
            file_options={"content-type": file.content_type}
        )

        url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(file_name)
        return url
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error has ocurred: {str(e)}")


def sv_delete_file(file_url: str) -> None:
    try:
        path = file_url.split(f"{SUPABASE_BUCKET}/")[-1]
        supabase.storage.from_(SUPABASE_BUCKET).remove([path])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error has ocurred: {str(e)}")
    

