"""
TDD Red Phase: User MBTI 기능 테스트

테스트 대상:
1. User 모델에 mbti, is_premium 필드 존재
2. MBTI 업데이트 API (PATCH /api/users/{user_id}/mbti)
3. 사용자 조회 시 MBTI 포함
"""
import pytest
from sqlalchemy import select

from app.models import User


class TestUserModel:
    """User 모델 테스트"""

    async def test_user_has_mbti_field(self, test_db):
        """User 모델에 mbti 필드가 있어야 한다"""
        user = User(
            google_id="test_google_123",
            email="test@example.com",
            name="Test User",
            mbti="ENFP",
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        assert user.mbti == "ENFP"

    async def test_user_has_is_premium_field(self, test_db):
        """User 모델에 is_premium 필드가 있어야 한다"""
        user = User(
            google_id="test_google_456",
            email="test2@example.com",
            name="Test User 2",
            is_premium=True,
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        assert user.is_premium is True

    async def test_user_mbti_default_is_none(self, test_db):
        """mbti 기본값은 None이어야 한다"""
        user = User(
            google_id="test_google_789",
            email="test3@example.com",
            name="Test User 3",
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        assert user.mbti is None

    async def test_user_is_premium_default_is_false(self, test_db):
        """is_premium 기본값은 False여야 한다"""
        user = User(
            google_id="test_google_000",
            email="test4@example.com",
            name="Test User 4",
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        assert user.is_premium is False


class TestMBTIUpdateAPI:
    """MBTI 업데이트 API 테스트"""

    async def test_update_user_mbti(self, client, test_db):
        """PATCH /api/users/{user_id}/mbti로 MBTI를 업데이트할 수 있어야 한다"""
        # Given: 사용자 생성
        user = User(
            google_id="api_test_123",
            email="api_test@example.com",
            name="API Test User",
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # When: MBTI 업데이트 API 호출
        response = await client.patch(
            f"/api/users/{user.id}/mbti",
            json={"mbti": "INTJ"},
        )

        # Then: 성공 응답
        assert response.status_code == 200
        data = response.json()
        assert data["mbti"] == "INTJ"

    async def test_update_mbti_invalid_type(self, client, test_db):
        """유효하지 않은 MBTI 타입은 422 에러를 반환해야 한다"""
        # Given: 사용자 생성
        user = User(
            google_id="api_test_456",
            email="api_test2@example.com",
            name="API Test User 2",
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # When: 잘못된 MBTI로 업데이트 시도
        response = await client.patch(
            f"/api/users/{user.id}/mbti",
            json={"mbti": "INVALID"},
        )

        # Then: 422 Unprocessable Entity (FastAPI validation error)
        assert response.status_code == 422

    async def test_update_mbti_user_not_found(self, client):
        """존재하지 않는 사용자 ID로 요청 시 404를 반환해야 한다"""
        import uuid

        fake_user_id = uuid.uuid4()
        response = await client.patch(
            f"/api/users/{fake_user_id}/mbti",
            json={"mbti": "ENFP"},
        )

        assert response.status_code == 404


class TestUserGetAPI:
    """사용자 조회 API 테스트"""

    async def test_get_user_includes_mbti(self, client, test_db):
        """GET /api/users/{user_id}로 사용자 조회 시 mbti가 포함되어야 한다"""
        # Given: MBTI가 설정된 사용자
        user = User(
            google_id="get_test_123",
            email="get_test@example.com",
            name="Get Test User",
            mbti="ISTP",
            is_premium=False,
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # When: 사용자 조회 API 호출
        response = await client.get(f"/api/users/{user.id}")

        # Then: mbti와 is_premium이 응답에 포함
        assert response.status_code == 200
        data = response.json()
        assert data["mbti"] == "ISTP"
        assert data["is_premium"] is False
