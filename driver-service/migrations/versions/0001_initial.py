"""Create driver-owned table."""
from alembic import op
import sqlalchemy as sa

revision = "0001_driver"
down_revision = None


def upgrade():
    op.create_table(
        "drivers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("driverid", sa.String(), nullable=False, unique=True),
        sa.Column("name", sa.String()), sa.Column("email", sa.String(), unique=True),
        sa.Column("mobile", sa.String(), unique=True), sa.Column("country", sa.String()),
        sa.Column("state", sa.String()), sa.Column("current_latitude", sa.Float()),
        sa.Column("current_longitude", sa.Float()), sa.Column("regions_available", sa.ARRAY(sa.String())),
        sa.Column("availability", sa.Boolean(), server_default=sa.true()),
        sa.Column("password", sa.String()), sa.Column("role", sa.String(), server_default="driver"),
        sa.Column("country_code", sa.String()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    for column in ("driverid", "name", "email", "country", "state", "availability", "role", "country_code"):
        op.create_index(f"ix_drivers_{column}", "drivers", [column], unique=column in {"driverid", "email"})


def downgrade():
    op.drop_table("drivers")
