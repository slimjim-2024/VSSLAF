from datetime import datetime, timezone
import os
from pathlib import Path
from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select
from slugify import slugify

from AgentCore import agents, custom_errors

# Single Database File for all Projects
db_folder = Path(Path.home(), "VSSLAF")
db_folder.mkdir(parents=True, exist_ok=True)
db_path = db_folder / "vsslaf.db"
engine = create_engine(f"sqlite:///{db_path}")


class ChatMessage(SQLModel, table=True):
    # Composite Primary Key: (project_id, message_id)
    project_id: UUID = Field(
        foreign_key="context.id",
        primary_key=True,
    )
    message_id: str = Field(
        primary_key=True,
        description="Auto-incremented string per project in format 'msg_0000001'",
    )

    role: str
    content: str
    agent_name: Optional[str] = Field(
        default=None,
        description="Identifies which specific agent generated this message",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Relationship back to Context
    context: Optional["Context"] = Relationship(back_populates="message_history")


class Context(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_name: str
    working_directory_str: Optional[str] = None

    # New requested columns
    date_created: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    ai_model_used: str = Field(default="gpt-4o")

    # Relationship to ChatMessages
    message_history: List[ChatMessage] = Relationship(
        back_populates="context",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "order_by": "ChatMessage.message_id"},
    )

    @property
    def working_directory(self) -> Optional[Path]:
        return Path(self.working_directory_str) if self.working_directory_str else None

    @working_directory.setter
    def working_directory(self, value: Optional[Path | str]) -> None:
        self.working_directory_str = str(value) if value else None

    @classmethod
    def create_context(
        cls,
        name: str,
        raw_path: Path | str,
        ai_model_used: str = "gemma4:12b",
    ) -> "Context":
        """Creates and persists a new Project Context into the shared database."""

        if not Path(raw_path).exists():
            raise custom_errors.InvalidArgumentType(
                f"{raw_path}", type(raw_path)
            )
        context = cls(
            project_name=name,
            working_directory_str=str(raw_path),
            ai_model_used=ai_model_used,
        )
        with Session(engine) as session:
            session.add(context)
            session.commit()
            session.refresh(context)
        return context

    @classmethod
    def load_data_from_db(cls) -> Optional["Context"]:
        """Displays all projects saved in the database and loads the selected project."""
        with Session(engine) as session:
            statement = select(cls).order_by(cls.date_created.desc())
            existing_contexts = session.exec(statement).all()

            if not existing_contexts:
                print("No saved projects found in the database.")
                return None

            print("\nOption | Project Name | AI Model | Date Created")
            print("-" * 65)
            for i, ctx in enumerate(existing_contexts):
                created_str = ctx.date_created.strftime("%Y-%m-%d %H:%M")
                print(f"{i + 1:6} | {ctx.project_name:18} | {ctx.ai_model_used:10} | {created_str}")

            choice = input("\nWhich project would you like to tackle this time? (leave empty to exit): ").strip()
            if not choice:
                return None

            while not choice.isdigit() or not (1 <= int(choice) <= len(existing_contexts)):
                print("Please choose a valid option number from the list.")
                choice = input("Which project would you like to tackle this time? (leave empty to exit): ").strip()
                if not choice:
                    return None

            selected_context = existing_contexts[int(choice) - 1]
            session.refresh(selected_context, ["message_history"])
            return selected_context

    def _generate_next_message_id(self, session: Session) -> str:
        """Calculates the next formatted message ID (e.g. msg_0000001) for this project."""
        statement = select(ChatMessage).where(ChatMessage.project_id == self.id)
        existing_messages = session.exec(statement).all()
        next_sequence = len(existing_messages) + 1
        return f"msg_{next_sequence:07d}"

    def append_message(
        self,
        role: str,
        content: str,
        agent_name: Optional[str] = None,
    ) -> ChatMessage:
        """Appends a new message with an auto-incremented message_id for this project."""
        with Session(engine) as session:
            next_msg_id = self._generate_next_message_id(session)
            message = ChatMessage(
                project_id=self.id,
                message_id=next_msg_id,
                role=role,
                content=content,
                agent_name=agent_name,
            )
            session.add(message)
            session.commit()
            session.refresh(message)

        # Sync local in-memory history list
        self.message_history.append(message)
        return message

    def set_path(self, path: Path | str) -> None:
        """Updates and persists the working directory path."""
        path_obj = Path(path)
        if path_obj.exists():
            self.working_directory_str = str(path_obj)
            with Session(engine) as session:
                session.add(self)
                session.commit()
        else:
            print("Path does not exist or is invalid.")


def init_db():
    """Initializes table schemas in SQLite."""
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    init_db()