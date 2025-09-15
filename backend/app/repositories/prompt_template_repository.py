from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.domain import PromptTemplate, PromptStatus

class PromptTemplateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_prompt_by_name(self, name: str) -> PromptTemplate | None:
        """
        Pobiera najnowszą, aktywną wersję promptu o podanej nazwie.
        """
        stmt = (
            select(PromptTemplate)
            .where(PromptTemplate.name == name, PromptTemplate.status == PromptStatus.ACTIVE)
            .order_by(PromptTemplate.version.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()