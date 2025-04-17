# anki-mcp-server

*다른 언어로 읽기: [English](../README.md), [한국어](README.md)*

Claude와 Anki를 연결하여 자연어로 플래시카드를 쉽게 생성할 수 있게 해주는 MCP(Model Context Protocol) 서버입니다.

## 소개

anki-mcp-server는 Claude와 Anki 앱 사이의 통신을 가능하게 하는 다리 역할을 합니다. 이를 통해 Claude에게 자연어로 명령을 내려 Anki 플래시카드를 생성하고 관리할 수 있습니다. 예를 들어, "일본어 쉬운단어 카드를 일본어 덱에 추가해줘"라고 요청하면 Claude가 알아서 적절한 카드를 생성합니다.

## 필수 조건

- Python 3.8 이상
- Anki 2.1.x 이상
- AnkiConnect 애드온
- Claude Desktop (또는 Claude API에 접근 가능한 환경)

## 설치 방법

### 1. Anki와 AnkiConnect 설정

1. [Anki](https://apps.ankiweb.net/)를 설치합니다.
2. AnkiConnect 애드온을 설치합니다:
   - Anki를 실행하고 상단 메뉴에서 `도구 > 애드온 > 애드온 찾아보기` 선택
   - 코드 `2055492159` 입력 후 '확인' 버튼 클릭
   - Anki를 재시작합니다

### 2. anki-mcp-server 설치

```bash
# 저장소 클론
git clone https://github.com/dhkim0124/anki-mcp-server.git
cd anki-mcp-server

# 가상환경 생성 및 활성화 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 필요한 패키지 설치
pip install -r requirements.txt
```

## 구성 방법

### Claude Desktop 설정

Claude Desktop의 설정 파일을 수정하여 MCP 서버를 등록합니다:

1. Claude Desktop 설정 파일 위치:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. 설정 파일에 다음 내용을 추가:

```json
{
  "mcpServers": {
    "anki-mcp": {
      "command": "python",
      "args": ["경로/anki_server.py"],
      "env": {}
    }
  }
}
```

`경로/anki_server.py`를 실제 anki_server.py 파일의 절대 경로로 변경하세요.

## 사용 방법

1. Anki 애플리케이션을 실행하고 백그라운드에서 실행 상태를 유지합니다.
2. Claude Desktop을 실행합니다.
3. Claude에게 다음과 같은 자연어 명령을 내릴 수 있습니다:

### 기본 명령 예시

- "일본어 쉬운단어 카드를 일본어 덱에 추가해줘"
- "영어 단어 'perseverance'의 뜻과 예문이 포함된 카드를 만들어줘"
- "오늘 배운 프로그래밍 개념을 정리해서 카드로 만들어줘"
- "역사 연대표 카드를 5개 만들어줘"

Claude는 이러한 요청을 해석하여 MCP 서버를 통해 Anki에 적절한 카드를 생성합니다.

## 주요 기능

### 카드 생성 기능

- 기본 질문-답변 형식의 카드 생성
- 특정 언어 학습용 카드 생성 (단어, 의미, 예문 포함)
- 자동 태그 추가
- 여러 덱에 카드 추가

### 덱 관리 기능

- 사용 가능한 덱 목록 확인
- 새로운 덱 생성
- 특정 덱의 카드 검색

## 문제 해결

### 연결 문제

- **Anki가 실행 중인지 확인**: MCP 서버가 Anki와 통신하기 위해서는 Anki가 실행 중이어야 합니다.
- **AnkiConnect 확인**: AnkiConnect가 제대로 설치되었는지 확인하세요. 웹 브라우저에서 `http://localhost:8765`에 접속하여 "AnkiConnect v.6" 메시지가 표시되는지 확인합니다.
- **방화벽 설정**: Windows 사용자의 경우 Anki에 대한 방화벽 액세스를 허용해야 할 수 있습니다.

### MCP 서버 문제

- **로그 확인**: 문제가 발생하면 서버 로그를 확인하여 오류 메시지를 확인하세요.
- **재시작**: 문제가 지속되면 Anki, Claude Desktop, MCP 서버를 모두 재시작해보세요.

## 확장 및 기여

프로젝트에 기여하고 싶으시다면 GitHub 저장소를 포크하고 풀 리퀘스트를 보내주세요. 다음과 같은 영역에서의 기여를 환영합니다:

- 새로운 카드 유형 지원
- 다양한 언어 지원 개선
- 인터페이스 개선
- 문서화 개선

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 LICENSE 파일을 참조하세요.

## 연락처

문제나 질문이 있으시면 GitHub 이슈를 통해 문의해주세요.
