import requests
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, HttpUrl

from src.backend.services import perso_service

router = APIRouter()


class DubbingRequest(BaseModel):
    url: HttpUrl


def handle_error(error):
    if isinstance(error, requests.exceptions.HTTPError):
        response = error.response
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text,
        ) from error
    if isinstance(error, requests.exceptions.RequestException):
        raise HTTPException(
            status_code=502,
            detail=f"Perso API 통신 오류: {error}",
        ) from error
    raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/dubbing", status_code=status.HTTP_202_ACCEPTED)
def create_dubbing(request: DubbingRequest):
    try:
        return perso_service.create_dubbing(str(request.url))
    except (requests.exceptions.RequestException, ValueError, KeyError) as error:
        handle_error(error)


@router.get("/dubbing/{project_seq}/progress")
def get_dubbing_progress(project_seq: int):
    try:
        return perso_service.get_progress(project_seq)
    except (requests.exceptions.RequestException, ValueError, KeyError) as error:
        handle_error(error)


@router.get("/dubbing/{project_seq}/result")
def get_dubbing_result(project_seq: int):
    try:
        progress = perso_service.get_progress(project_seq)
        if progress.get("progressReason") != "Completed":
            return {
                "projectSeq": project_seq,
                "status": progress.get("progressReason"),
                "videoUrl": None,
            }
        return {
            "projectSeq": project_seq,
            "status": "Completed",
            "videoUrl": perso_service.get_result_url(project_seq),
        }
    except (requests.exceptions.RequestException, ValueError, KeyError) as error:
        handle_error(error)
