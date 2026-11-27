# perso_service.py
# 페르소 url 더빙 -> url

import httpx
from fastapi import HTTPException
from urllib.parse import quote
from src.backend.core.config import (
    PERSO_BASE_URL,
    PERSO_MEDIA_URL,
    PERSO_API_KEY,
    PERSO_SPACE_SEQ
)

# 외부 HTTP 비동기 클라이언트 생성
def make_client(timeout: float = 600.0) -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=timeout, follow_redirects=False)

# 외부 응답의 JSON 본문과 HTTP 오류를 일관되게 처리
# 일부 오류가 JSON이 아닐 수 있으므로 문자열로도 안전하게 처리
def parse_response(response: httpx.Response) -> dict:
    try:
        data = response.json() if response.content else {}
    except ValueError:
        data = {'message': response.text[:120]}
    if response.status_code >= 400:
        err = data if isinstance(data, dict) else {'message': str(data)}
        raise HTTPException(
            status_code=response.status_code,
            detail={
                'code': err.get('code', ''),
                'detailCode': err.get('detailCode', ''),
                'message': err.get('message', err.get('detail',
                                                    '외부 routers 오류')),
            },
        )
    if not isinstance(data, dict):
        raise HTTPException(502, '예상하지 못한 Perso 응답 형식')
    return data

# Perso api 서버에 KEY 헤더를 붙여 실제 HTTP 요청 전송
async def perso_call(method: str, path: str, *, params=None, json=None) -> dict:
    if not PERSO_API_KEY:
        raise HTTPException(503, 'PERSO_API_KEY 환경 변수가 없습니다')
    try:
        async with make_client() as client:
            response = await client.request(
                method, PERSO_BASE_URL + path, params=params, json=json,
                headers={'XP-API-KEY': PERSO_API_KEY},
            )
    except httpx.TimeoutException as exc:
        raise HTTPException(504, 'Perso routers 요청 시간 초과') from exc
    except httpx.RequestError as exc:
        raise HTTPException(502, 'Perso routers 연결 오류') from exc
    return parse_response(response)

# 1. 외부영상 메타데이터 가져오기
async def get_metadata(url):
    return await perso_call(
        'POST',
        '/file/api/v1/video-translator/external/metadata',
        json={
            'spaceSeq': PERSO_SPACE_SEQ,
            'url': url,
            'lang': 'en',
            'sttMode': False
        }
    )

# 2. 유효성 검사
async def validate_video(metadata):
    return await perso_call(
        'POST',
        '/file/api/v1/media/validate',
        json={
            'spaceSeq': PERSO_SPACE_SEQ,
            'durationMs': metadata['durationMs'],
            'originalName': metadata['originalName'],
            'mediaType': metadata['mediaType'],
            'extension': metadata['extension'],
            'width': metadata['width'],
            'height': metadata['height'],
            'sttMode': False
        }
    )

# 외부영상 업로드
async def upload_video(url):
    result = await perso_call(
        'PUT',
        '/file/api/upload/video/external',
        json={
            'spaceSeq': PERSO_SPACE_SEQ,
            'url': url,
            'lang': 'en',
            'sttMode': False
        },
    )
    return result['seq']

# 초기화
async def initialize_queue():
    return await perso_call(
        "PUT",
        f"/video-translator/api/v1/projects/spaces/{PERSO_SPACE_SEQ}/queue",
    )

# 더빙 요청 본문 만들고 첫 projectSeq반환
async def dubbing(media_seq):
    result = await perso_call(
        'POST',
        f'/video-translator/api/v1/projects/spaces/{PERSO_SPACE_SEQ}/translate',
        json={
            'mediaSeq': media_seq,
            'isVideoProject': True,
            'sourceLanguageCode': 'auto',
            'targetLanguages': [{'languageCode': 'ko'}],
            'numberOfSpeakers': 1,
            'preferredSpeedType': 'GREEN',
            'withLipSync': False,
            'title': 'Soccer Highlight'
        }
    )
    return result['result']['startGenerateProjectIdList'][0]

# 더빙 생성 요청
async def create_dubbing(video_url):
    metadata = await get_metadata(video_url)
    validation = await validate_video(metadata)
    if not validation.get("status"):
        raise HTTPException(422, "영상 유효성 검사 실패")

    media_seq = await upload_video(video_url)
    await initialize_queue()
    project_seq = await dubbing(media_seq)

    return {
        "mediaSeq": media_seq,
        "projectSeq": project_seq,
        "status": "requested"
    }

# 진행상황 가져오기
async def get_progress(project_seq):
    result = await perso_call(
        "GET",
        f"/video-translator/api/v1/projects/{project_seq}/space/{PERSO_SPACE_SEQ}/progress",
    )
    return result["result"]

# 결과 url
async def get_result_url(project_seq):
    info = await perso_call(
        "GET",
        f"/video-translator/api/v1/projects/{project_seq}/spaces/{PERSO_SPACE_SEQ}/download-info",
    )
    if not info.get("result", {}).get('hasTranslatedVideo'):
        return None

    result = await perso_call(
        "GET",
        f"/video-translator/api/v1/projects/{project_seq}/spaces/{PERSO_SPACE_SEQ}/download",
        params={"target": "dubbingVideo"},
    )
    path = result["result"]["videoFile"]["videoDownloadLink"]
    if path.startswith("https://"):
        return path
    return PERSO_MEDIA_URL + quote("/" + path.lstrip("/"), safe="/%")




















































