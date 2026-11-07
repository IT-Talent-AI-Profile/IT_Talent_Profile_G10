
import json
import pytest
import requests

from unittest.mock import Mock
from pydantic import ValidationError

from app.schemas.cv import CvResult
from app.services import ai_client


def test_extract_cv_mock(monkeypatch):
    monkeypatch.setattr(ai_client.settings, "AI_MODE", "mock")
    monkeypatch.setattr(ai_client.settings, "AI_API_KEY", "")

    result = ai_client.extract_cv("CV mẫu", ["Python", "Java"])

    assert isinstance(result, CvResult)
    assert len(result.skills) > 0
    assert result.skills[0].name == "Python"


def test_make_summary():
    result = ai_client.make_summary()

    assert isinstance(result, str)
    assert len(result.strip()) > 0


def test_extract_cv_empty():
    with pytest.raises(ValueError):
        ai_client.extract_cv("", ["Python"])


def test_parse_valid_json():
    response = json.dumps({
        "skills": [
            {
                "name": "Python",
                "proficiency": 3,
                "years": 1
            }
        ],
        "years_experience": 1,
        "education": "Đại học",
        "experience": "Lập trình viên"
    })

    result = ai_client._parse_ai_response(response)

    assert isinstance(result, CvResult)
    assert result.skills[0].name == "Python"


def test_parse_invalid_json():
    with pytest.raises(json.JSONDecodeError):
        ai_client._parse_ai_response("{invalid json}")


def test_parse_invalid_schema():
    response = json.dumps({
        "skills": [
            {
                "name": "Python",
                "proficiency": 10,
                "years": 1
            }
        ]
    })

    with pytest.raises(ValidationError):
        ai_client._parse_ai_response(response)


def test_extract_cv_retry(monkeypatch):
    monkeypatch.setattr(ai_client.settings, "AI_MODE", "real")
    monkeypatch.setattr(ai_client.settings, "AI_API_KEY", "test-key")

    mock_call = Mock(return_value="{invalid json}")

    monkeypatch.setattr(ai_client, "call_ai", mock_call)

    with pytest.raises(ValueError):
        ai_client.extract_cv("CV mẫu", ["Python"])

    assert mock_call.call_count == 3


def test_call_ai_timeout(monkeypatch):
    monkeypatch.setattr(ai_client.settings, "AI_API_KEY", "test-key")

    def fake_post(*args, **kwargs):
        assert kwargs["timeout"] == 30
        raise requests.Timeout()

    monkeypatch.setattr(ai_client.requests, "post", fake_post)

    with pytest.raises(RuntimeError, match="30 giây"):
        ai_client.call_ai("Prompt test")


def test_extract_cv_filters_skills(monkeypatch):
    monkeypatch.setattr(ai_client.settings, "AI_MODE", "real")
    monkeypatch.setattr(ai_client.settings, "AI_API_KEY", "test-key")

    response = json.dumps({
        "skills": [
            {
                "name": "Python",
                "proficiency": 3,
                "years": 1
            },
            {
                "name": "Java",
                "proficiency": 4,
                "years": 2
            }
        ],
        "years_experience": 2,
        "education": "Đại học",
        "experience": "Lập trình viên"
    })

    monkeypatch.setattr(
        ai_client,
        "call_ai",
        lambda prompt: response
    )

    result = ai_client.extract_cv("CV mẫu", ["Python"])

    assert len(result.skills) == 1
    assert result.skills[0].name == "Python"


def test_extract_cv_limits_cv_length(monkeypatch):
    monkeypatch.setattr(ai_client.settings, "AI_MODE", "real")
    monkeypatch.setattr(ai_client.settings, "AI_API_KEY", "test-key")

    captured = {}

    def fake_prompt(cv_text, skill_catalog):
        captured["length"] = len(cv_text)
        return "Prompt test"

    response = json.dumps({
        "skills": [],
        "years_experience": 0,
        "education": None,
        "experience": None
    })

    monkeypatch.setattr(
        ai_client,
        "build_cv_extraction_prompt",
        fake_prompt
    )

    monkeypatch.setattr(
        ai_client,
        "call_ai",
        lambda prompt: response
    )

    ai_client.extract_cv("A" * 15000, ["Python"])

    assert captured["length"] == 12000


def test_call_ai_success(monkeypatch):
    monkeypatch.setattr(
        ai_client.settings,
        "AI_API_KEY",
        "test-key"
    )

    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "content": [
                    {
                        "type": "text",
                        "text": '{"skills": []}'
                    }
                ]
            }

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured["headers"] = kwargs["headers"]
        captured["payload"] = kwargs["json"]
        captured["timeout"] = kwargs["timeout"]
        return FakeResponse()

    monkeypatch.setattr(
        ai_client.requests,
        "post",
        fake_post
    )

    result = ai_client.call_ai("Prompt kiểm tra")

    assert result == '{"skills": []}'
    assert captured["url"] == ai_client.ANTHROPIC_API_URL
    assert captured["headers"]["x-api-key"] == "test-key"
    assert captured["headers"]["anthropic-version"] == ai_client.ANTHROPIC_VERSION
    assert captured["payload"]["model"] == ai_client.ANTHROPIC_MODEL
    assert captured["payload"]["messages"][0]["content"] == "Prompt kiểm tra"
    assert captured["timeout"] == 30


def test_build_prompt_contains_cv_and_catalog():
    from app.services.prompts import build_cv_extraction_prompt

    prompt = build_cv_extraction_prompt(
        cv_text="Tôi có 2 năm kinh nghiệm Python",
        skill_catalog=["Python", "Java"]
    )

    assert "Tôi có 2 năm kinh nghiệm Python" in prompt
    assert "Python" in prompt
    assert "Java" in prompt
    assert "JSON hợp lệ" in prompt
    assert "Không tự tạo thêm kỹ năng" in prompt


def test_build_prompt_rejects_empty_cv():
    from app.services.prompts import build_cv_extraction_prompt

    with pytest.raises(ValueError):
        build_cv_extraction_prompt("", ["Python"])
