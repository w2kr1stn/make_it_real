FROM python:3.13-alpine3.22
RUN apk add --update --no-cache uv
COPY pyproject.toml uv.lock README.md /make_it_real/
WORKDIR /make_it_real
RUN uv sync
COPY . .
ENTRYPOINT ["uv", "run", "makeitreal"]
CMD ["task management app for developers"]
