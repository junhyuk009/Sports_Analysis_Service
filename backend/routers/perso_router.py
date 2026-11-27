# perso_router.py

import requests
from fastapi import APIRouter, HTTPException, status, FastAPI
from pydantic import BaseModel, HttpUrl
from service import perso_service

PREFIX = '/video-translator/api/v1'

# 451858

app = FastAPI(
    title='Test',
    version='0.0.1'
)

perso_router = APIRouter(
    prefix='/api/v1/perso',
    tags=['perso']
)

class DubbingRequest(BaseModel):
    url: HttpUrl

# 더빙 등록
@perso_router.post('/dubbing', status_code=status.HTTP_201_CREATED)
async def create_dubbing(request: DubbingRequest):
    try:
        return await perso_service.create_dubbing(str(request.url))
    except (requests.exceptions.RequestException, ValueError):
        raise HTTPException(422, "영상 유효성 검사 실패")

# 더빙 진행 상황
@perso_router.get('/dubbing/{project_seq}/progress')
async def get_dubbing(project_seq: int):
    try:
        return await perso_service.get_progress(project_seq)
    except (requests.exceptions.RequestException, ValueError):
        raise HTTPException(404, '해당 프로젝트를 찾을 수 없습니다')

# 더빙 결과 url
@perso_router.get('/dubbing/{project_seq}/results')
async def dubbing_result(project_seq: int):
    try:
        progress = await perso_service.get_progress(project_seq)
        if progress.get('progressReason') != 'Completed':
            return {
                'projectSeq': project_seq,
                'status': progress.get('progressReason'),
                'videoUrl': None
            }
        return {
            'projectSeq': project_seq,
            'status': progress.get('progressReason'),
            'videoUrl': await perso_service.get_result_url(project_seq)
        }
    except (requests.exceptions.RequestException, ValueError):
        raise HTTPException(404, '해당 프로젝트를 찾을 수 없습니다')


# test
@perso_router.get('/perso/spaces/{space_seq}/projects/{project_seq}/files')
async def files(
    space_seq: int,
    project_seq: int
):
    return await perso_service.perso_call(
        'GET',
        f'{PREFIX}/projects/{project_seq}/spaces/{space_seq}/download-info'
    )




app.include_router(perso_router)



























































































































