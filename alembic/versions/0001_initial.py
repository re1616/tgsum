from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("phone", sa.String(32), unique=True),
        sa.Column("tz", sa.String(64)),
        sa.Column("digest_hour", sa.Integer),
        sa.Column("max_items", sa.Integer),
        sa.Column("min_score", sa.Float),
        sa.Column("bot_chat_id", sa.String(64), unique=True),
        sa.Column("link_code", sa.String(16), unique=True),
        sa.Column("topics", sa.Text),
        sa.Column("exclude_channels", sa.Text),
        sa.Column("languages", sa.String(64)),
        sa.Column("quiet_hours", sa.String(32)),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_table("tg_sessions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), unique=True),
        sa.Column("session_encrypted", sa.Text),
    )
    op.create_table("messages",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, index=True),
        sa.Column("channel_id", sa.Integer, index=True),
        sa.Column("msg_id", sa.Integer),
        sa.Column("date", sa.DateTime(timezone=True), index=True),
        sa.Column("text", sa.Text),
        sa.Column("views", sa.Integer),
        sa.Column("forwards", sa.Integer),
        sa.Column("reactions", sa.Integer),
        sa.Column("comments", sa.Integer),
        sa.Column("lang", sa.String(8)),
        sa.Column("score", sa.Float),
    )
    op.create_table("digests",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, index=True),
        sa.Column("date", sa.DateTime(timezone=True), index=True),
        sa.Column("delivered", sa.Boolean),
    )
    op.create_table("digest_items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("digest_id", sa.Integer, index=True),
        sa.Column("channel_id", sa.Integer),
        sa.Column("msg_id", sa.Integer),
        sa.Column("title", sa.String(256)),
        sa.Column("summary", sa.Text),
        sa.Column("score", sa.Float, index=True),
    )

def downgrade():
    op.drop_table("digest_items")
    op.drop_table("digests")
    op.drop_table("messages")
    op.drop_table("tg_sessions")
    op.drop_table("users")
