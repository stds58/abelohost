FROM python:3.13-slim AS builder

ARG WORKDIR=/opt/abelo

WORKDIR $WORKDIR
RUN pip install uv
ENV PATH="$WORKDIR/.venv/bin:$PATH"

COPY ../pyproject.toml .
RUN uv sync --group main
#RUN uv sync --group main --group linter

FROM python:3.13-slim

ARG WORKDIR=/opt/abelo
ARG USER=appuser

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR $WORKDIR

COPY --from=builder $WORKDIR/.venv $WORKDIR/.venv
ENV PATH="$WORKDIR/.venv/bin:$PATH"

RUN useradd -m appuser

COPY ./backend ./backend

COPY backend/entrypoint.sh /opt/abelo/backend/entrypoint.sh
RUN chmod +x /opt/abelo/backend/entrypoint.sh

USER appuser

ENTRYPOINT ["/opt/abelo/backend/entrypoint.sh"]
