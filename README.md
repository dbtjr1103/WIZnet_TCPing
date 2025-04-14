# WIZnet TCPing

TCP 연결 테스트를 위한 간단한 GUI 유틸리티입니다. 특정 IP 주소와 포트에 대해 TCP 연결 테스트를 수행하고 결과와 통계를 표시합니다.

## 주요 기능

- TCP 연결 테스트
- 연결 성공/실패 표시
- 응답 시간 측정 (밀리초 단위)
- 통계 정보 표시 (최소/최대/평균 시간)

## 스크린샷

![WIZnet TCPing 스크린샷](screenshot.png)

## 설치 방법

### 방법 1: 실행 파일 다운로드

1. [릴리스 페이지](https://github.com/yourusername/wiznet-tcping/releases)에서 최신 버전의 `WIZnet_TCPing.exe` 파일을 다운로드합니다.
2. 다운로드 받은 파일을 실행합니다.

### 방법 2: 소스에서 빌드

필요한 패키지:
- Python 3.6 이상
- tkinter (대부분의 Python 설치에 포함됨)

```bash
# 저장소 클론
git clone https://github.com/yourusername/wiznet-tcping.git
cd wiznet-tcping

# 필요한 패키지 설치
pip install -r requirements.txt

# 프로그램 실행
python tcping_gui.py
```

실행 파일 생성:
```bash
# PyInstaller가 설치되어 있지 않은 경우
pip install pyinstaller

# 실행 파일 생성
pyinstaller --onefile --windowed --name "WIZnet_TCPing" tcping_gui.py
```

## 사용 방법

1. IP 주소 입력란에 테스트할 장치의 IP 주소를 입력합니다 (예: `192.168.11.2`).
2. 포트 입력란에 테스트할 포트 번호를 입력합니다 (예: `5000`).
3. Count 입력란에 연결 시도 횟수를 설정합니다 (0은 무제한).
4. Start 버튼을 클릭하여 테스트를 시작합니다.
5. 테스트 중에는 Stop 버튼을 클릭하여 중지할 수 있습니다.
6. Reset 버튼을 클릭하여 입력 필드와 결과를 초기화합니다.
7. 프로그램을 종료하려면 창의 X 버튼을 클릭하세요.

## 테스트 결과 해석

- 성공한 연결: `Probing <IP 주소>:<포트>/tcp - Port is open - time=<응답 시간>ms`
- 실패한 연결: `Probing <IP 주소>:<포트>/tcp - Port is closed - <오류 코드>`
- 타임아웃: `Probing <IP 주소>:<포트>/tcp - Timeout`

테스트 종료 후에는 다음과 같은 통계 정보가 표시됩니다:
- 전송된 프로브 수
- 성공/실패 연결 수 및 실패율
- 최소/최대/평균 응답 시간 (밀리초 단위)

## 개발자 정보

이 프로그램은 WIZnet의 TCP/IP 솔루션 테스트를 위해 개발되었습니다.

## 라이선스

MIT License 