import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserGallery(Base):
    """
    사용자 갤러리 - 세션 삭제와 무관하게 이미지 보관

    image_type:
    - 'expression': 6감정 이미지 (비프리미엄도 blur 없음)
    - 'special': 특별 이벤트 이미지 (비프리미엄은 blur)
    - 'ending': 엔딩 이미지 (비프리미엄은 blur)
    """
    __tablename__ = "user_gallery"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    image_url: Mapped[str] = mapped_column(Text)
    image_type: Mapped[str] = mapped_column(String(20))  # 'expression', 'special', 'ending'
    expression_type: Mapped[str] = mapped_column(String(20), nullable=True)  # 'neutral', 'happy', etc.
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="gallery_images")
