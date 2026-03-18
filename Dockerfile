FROM python:3.11.15-slim-trixie

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip "wheel>=0.46.3" "setuptools>=82.0.1"
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

RUN useradd -m -u 1000 user

COPY --chown=user:user . .

USER user

ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

CMD ["uvicorn","Server:app","--host","0.0.0.0","--port","7860"]