"""Create user-owned tables."""
from alembic import op
import sqlalchemy as sa

revision = "0001_user"
down_revision = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("userid", sa.String(), nullable=False, unique=True),
        sa.Column("name", sa.String()), sa.Column("email", sa.String(), unique=True),
        sa.Column("country", sa.String()), sa.Column("state", sa.String()),
        sa.Column("country_code", sa.String()), sa.Column("phone_number", sa.String(), unique=True),
        sa.Column("password", sa.String()), sa.Column("role", sa.String()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "booking_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("booking_id", sa.String(), nullable=False, unique=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.userid")),
        sa.Column("vehicle_id", sa.String()), sa.Column("driver_id", sa.String()),
        sa.Column("driver_name", sa.String()), sa.Column("driver_email", sa.String()), sa.Column("driver_mobile", sa.String()),
        sa.Column("pickup_location", sa.String()), sa.Column("pickup_latitude", sa.Float()), sa.Column("pickup_longitude", sa.Float()),
        sa.Column("drop_location", sa.String()), sa.Column("drop_latitude", sa.Float()), sa.Column("drop_longitude", sa.Float()),
        sa.Column("distance_to_cover", sa.Float()), sa.Column("estimated_delivery_time", sa.Float()),
        sa.Column("base_price", sa.Float()), sa.Column("gst", sa.Float()), sa.Column("platform_fee", sa.Float()), sa.Column("total_price", sa.Float()),
        sa.Column("request_status", sa.String(), server_default="Pending"),
        sa.Column("delivery_status", sa.String(), server_default="Pending Pickup"),
        sa.Column("order_status", sa.String(), server_default="Pending"),
        sa.Column("payment_status", sa.String(), server_default="Completed"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    for table, columns in {"users": ("userid", "email", "phone_number", "role"), "booking_requests": ("booking_id", "user_id", "vehicle_id", "driver_id")}.items():
        for column in columns:
            op.create_index(f"ix_{table}_{column}", table, [column], unique=column in {"userid", "email", "phone_number", "booking_id"})


def downgrade():
    op.drop_table("booking_requests")
    op.drop_table("users")
