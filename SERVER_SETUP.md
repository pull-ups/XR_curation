# 서버 설정 가이드

이 문서는 `api.py`를 실행하기 위한 간단한 설정 가이드입니다.

## 1. OpenAI API 키 설정

서버를 실행하기 전에 OpenAI API 키를 환경 변수로 설정해야 합니다.

### macOS / Linux

터미널에서 다음 명령어를 실행하세요:

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

이 설정은 현재 터미널 세션에서만 유효합니다. 영구적으로 설정하려면 `~/.zshrc` (zsh 사용 시) 또는 `~/.bashrc` (bash 사용 시) 파일에 추가하세요:

```bash
echo 'export OPENAI_API_KEY="your-openai-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### Windows

PowerShell에서:
```powershell
$env:OPENAI_API_KEY="your-openai-api-key-here"
```

또는 명령 프롬프트에서:
```cmd
set OPENAI_API_KEY=your-openai-api-key-here
```

## 2. 의존성 설치

필요한 패키지를 설치합니다:

```bash
pip install -r requirements.txt
```

## 3. 서버 실행

### localhost로 실행 (로컬 환경)

프로젝트 루트 디렉토리에서 다음 명령어를 실행하세요:

```bash
python api.py
```

서버가 시작되면 다음 주소에서 접근할 수 있습니다:
- **웹 인터페이스**: http://localhost:14723/
- **API 문서 (Swagger)**: http://localhost:14723/docs
- **API 문서 (ReDoc)**: http://localhost:14723/redoc

### 외부 접근 허용 (ngrok 사용)

외부에서 API에 접근하려면 ngrok을 사용할 수 있습니다.

#### ngrok 설치

1. [ngrok 공식 웹사이트](https://ngrok.com/)에서 가입
2. [다운로드 페이지](https://ngrok.com/download)에서 ngrok 다용할 수 있는 버전 다운로드
3. 다운로드한 파일을 압축 해제하고 실행 파일을 시스템 PATH에 추가하거나 현재 디렉토리에 둡니다.

#### ngrok 설정

ngrok 사용을 위해서는 먼저 인증 토큰을 설정해야 합니다. ngrok 웹사이트에서 받은 인증 토큰을 사용하세요:

```bash
ngrok config add-authtoken YOUR_NGROK_AUTH_TOKEN
```

#### 서버 및 ngrok 실행

**방법 1: 터미널 두 개 사용**

터미널 1: API 서버 실행
```bash
python api.py
```

터미널 2: ngrok 실행
```bash
ngrok http 14723
```

**방법 2: 제공된 스크립트 사용 (ngrok 인증 토큰이 이미 설정된 경우)**

먼저 `ngrok.sh` 파일을 확인하고, 인증 토큰이 이미 설정되어 있다면:

```bash
bash ngrok.sh
```

> **참고**: `ngrok.sh` 파일에 있는 인증 토큰은 예시일 수 있으므로, 실제 본인의 ngrok 인증 토큰을 사용하세요.

#### ngrok 사용 시 접근 방법

ngrok이 실행되면 다음과 같은 출력이 나타납니다:

```
Forwarding   https://xxxx-xxxx-xxxx.ngrok-free.app -> http://localhost:14723
```

이 경우 외부 접근은 `https://xxxx-xxxx-xxxx.ngrok-free.app` 주소로 가능합니다.

## 4. 서버 상태 확인

서버가 정상적으로 실행되었는지 확인하려면:

```bash
curl http://localhost:14723/ping
```

또는 브라우저에서 http://localhost:14723/ping 접속

정상 응답 예시:
```json
{
  "message": "pong",
  "status": "healthy",
  "curation_types_loaded": true,
  "touch_recognition_loaded": true
}
```

## 문제 해결

### OpenAI API 키 관련 오류

에러 메시지: `OpenAI API 키가 설정되지 않았습니다.`

해결 방법:
1. 환경 변수 `OPENAI_API_KEY`가 올바르게 설정되었는지 확인
2. 터미널에서 `echo $OPENAI_API_KEY` (macOS/Linux) 또는 `echo %OPENAI_API_KEY%` (Windows)로 확인

### 포트 14723이 이미 사용 중인 경우

다른 프로세스가 해당 포트를 사용 중일 수 있습니다. 포트를 변경하려면 `api.py` 파일의 마지막 줄을 수정하세요:

```python
uvicorn.run(app, host="0.0.0.0", port=원하는포트번호)
```

