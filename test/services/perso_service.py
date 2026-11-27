from urllib.parse import quote

import requests

from core.config import (
    PERSO_BASE_URL,
    PERSO_MEDIA_URL,
    PERSO_API_KEY,
    PERSO_SPACE_SEQ
)


def perso_request(method, endpoint, timeout=30, **kwargs):
    if not PERSO_API_KEY or not PERSO_SPACE_SEQ:
        raise ValueError("Perso API 환경변수를 확인하세요.")

    response = requests.request(
        method,
        f"{PERSO_BASE_URL}{endpoint}",
        headers={"XP-API-KEY": PERSO_API_KEY},
        timeout=timeout,
        **kwargs,
    )
    response.raise_for_status()
    return response.json()


def get_video_metadata(video_url):
    return perso_request(
        "POST",
        "/file/api/v1/video-translator/external/metadata",
        json={
            "spaceSeq": PERSO_SPACE_SEQ,
            "url": video_url,
            "lang": "en",
            "sttMode": False,
        },
    )


def validate_video(metadata):
    return perso_request(
        "POST",
        "/file/api/v1/media/validate",
        json={
            "spaceSeq": PERSO_SPACE_SEQ,
            "durationMs": metadata["durationMs"],
            "originalName": metadata["originalName"],
            "mediaType": "video",
            "extension": metadata["extension"],
            "size": metadata.get("size"),
            "width": metadata["width"],
            "height": metadata["height"],
            "sttMode": False,
        },
    )


def upload_video(video_url):
    result = perso_request(
        "PUT",
        "/file/api/upload/video/external",
        timeout=660,
        json={
            "spaceSeq": PERSO_SPACE_SEQ,
            "url": video_url,
            "lang": "en",
            "sttMode": False,
        },
    )
    return result["seq"]


def initialize_queue():
    return perso_request(
        "PUT",
        f"/video-translator/api/v1/projects/spaces/{PERSO_SPACE_SEQ}/queue",
    )


def start_dubbing(media_seq):
    result = perso_request(
        "POST",
        f"/video-translator/api/v1/projects/spaces/{PERSO_SPACE_SEQ}/translate",
        json={
            "mediaSeq": media_seq,
            "isVideoProject": True,
            "sourceLanguageCode": "auto",
            "targetLanguages": [{"languageCode": "ko"}],
            "numberOfSpeakers": 1,
            "preferredSpeedType": "GREEN",
            "withLipSync": False,
            "title": "Football Highlights Korean Dubbing",
        },
    )
    return result["result"]["startGenerateProjectIdList"][0]


def create_dubbing(video_url):
    metadata = get_video_metadata(video_url)
    validation = validate_video(metadata)
    if not validation.get("status"):
        raise ValueError("영상 유효성 검사 실패")

    media_seq = upload_video(video_url)
    initialize_queue()
    project_seq = start_dubbing(media_seq)

    return {
        "mediaSeq": media_seq,
        "projectSeq": project_seq,
        "status": "requested",
    }


def get_progress(project_seq):
    result = perso_request(
        "GET",
        f"/video-translator/api/v1/projects/{project_seq}/space/{PERSO_SPACE_SEQ}/progress",
    )
    return result["result"]


def get_result_url(project_seq):
    info = perso_request(
        "GET",
        f"/video-translator/api/v1/projects/{project_seq}/spaces/{PERSO_SPACE_SEQ}/download-info",
    )
    if not info.get("hasTranslatedVideo"):
        return None

    result = perso_request(
        "GET",
        f"/video-translator/api/v1/projects/{project_seq}/spaces/{PERSO_SPACE_SEQ}/download",
        params={"target": "dubbingVideo"},
    )
    path = result["result"]["videoFile"]["videoDownloadLink"]
    if path.startswith("https://"):
        return path
    return PERSO_MEDIA_URL + quote("/" + path.lstrip("/"), safe="/%")
