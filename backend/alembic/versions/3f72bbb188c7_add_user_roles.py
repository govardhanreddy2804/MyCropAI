"""Add user roles

Revision ID: 3f72bbb188c7
Revises: b5d34300c6e6
Create Date: 2026-08-26 09:44:32.500854

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "3f72bbb188c7"
down_revision: Union[str, Sequence[str], None] = "b5d34300c6e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Convert existing role values to the new enum labels.
    op.execute(
        "UPDATE users SET role = UPPER(role)"
    )

    # Create the PostgreSQL enum type.
    user_role_enum = postgresql.ENUM(
        "ADMIN",
        "FARMER",
        "AGRONOMIST",
        name="userrole",
    )

    user_role_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    # Convert the users.role column from VARCHAR to the enum.
    op.alter_column(
        "users",
        "role",
        existing_type=sa.VARCHAR(length=30),
        type_=user_role_enum,
        existing_nullable=False,
        postgresql_using="role::text::userrole",
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Convert enum back to VARCHAR.
    op.alter_column(
        "users",
        "role",
        existing_type=postgresql.ENUM(
            "ADMIN",
            "FARMER",
            "AGRONOMIST",
            name="userrole",
        ),
        type_=sa.VARCHAR(length=30),
        existing_nullable=False,
        postgresql_using="role::text",
    )

    # Remove the PostgreSQL enum type.
    user_role_enum = postgresql.ENUM(
        "ADMIN",
        "FARMER",
        "AGRONOMIST",
        name="userrole",
    )

    user_role_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )