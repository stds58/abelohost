FROM python:3.13-slim AS builder

ARG WORKDIR=/opt/abelo

WORKDIR $WORKDIR
RUN pip install uv
ENV PATH="$WORKDIR/.venv/bin:$PATH"

COPY ../pyproject.toml .
RUN uv sync --group main

FROM python:3.13-slim

ARG WORKDIR=/opt/abelo
ARG USER=appuser
ARG UID=1000
ARG GID=1000

# Создаем непривилегированного пользователя БЕЗ доступа к shell
# --no-create-home: нам не нужен home dir, мы работаем в WORKDIR
# --shell /sbin/nologin: защита от интерактивного входа
RUN groupadd --gid ${GID} ${USER} \
    && useradd --uid ${UID} --gid ${GID} --no-create-home --shell /sbin/nologin ${USER}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=${WORKDIR} \
    WORKDIR=${WORKDIR} \
    PATH="${WORKDIR}/.venv/bin:$PATH"

WORKDIR $WORKDIR

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder $WORKDIR/.venv $WORKDIR/.venv
COPY backend/ ${WORKDIR}/backend/
COPY backend/entrypoint.sh ${WORKDIR}/entrypoint.sh

RUN chmod +x ${WORKDIR}/entrypoint.sh \
    && chown ${UID}:${GID} ${WORKDIR}/entrypoint.sh \
    && mkdir -p ${WORKDIR}/.cache ${WORKDIR}/tmp /tmp /run \
    && chown -R ${UID}:${GID} ${WORKDIR} \
    && chmod 1777 /tmp \
    && chmod 755 /run

USER ${UID}:${GID}

ENTRYPOINT ["/opt/abelo/backend/entrypoint.sh"]
