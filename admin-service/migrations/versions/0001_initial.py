"""Create admin-owned table."""
from alembic import op
import sqlalchemy as sa

revision = "0001_admin"
down_revision = None


def upgrade():
    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("vehicleid", sa.String(), nullable=False, unique=True),
        sa.Column("model_name", sa.String()), sa.Column("capacity_in_kg", sa.Float()),
        sa.Column("registration_number", sa.String(), unique=True),
        sa.Column("current_latitude", sa.Float()), sa.Column("current_longitude", sa.Float()),
        sa.Column("is_available", sa.Boolean(), server_default=sa.true()),
        sa.Column("active_status", sa.Boolean(), server_default=sa.false()),
        sa.Column("fuel_type", sa.String()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    for column in ("vehicleid", "registration_number", "fuel_type"):
        op.create_index(f"ix_vehicles_{column}", "vehicles", [column], unique=column in {"vehicleid", "registration_number"})


def downgrade():
    op.drop_table("vehicles")
