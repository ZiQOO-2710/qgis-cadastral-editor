"""
프로젝트 설정 및 경로 관리 모듈

환경변수를 읽어서 프로젝트 전체에서 사용할 경로와 설정을 관리합니다.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).parent.absolute()

# 환경변수에서 경로 읽기 (없으면 기본값 사용)
PROJECT_DIR = Path(os.getenv('PROJECT_DIR', PROJECT_ROOT))
DATA_DIR = Path(os.getenv('DATA_DIR', PROJECT_ROOT / 'data'))
INPUT_DIR = Path(os.getenv('INPUT_DIR', PROJECT_ROOT / 'input'))
OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', PROJECT_ROOT / 'output'))

# 디렉토리 존재 확인 및 생성
for directory in [DATA_DIR, INPUT_DIR, OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# QGIS 설정
QGIS_PREFIX_PATH = os.getenv('QGIS_PREFIX_PATH', '/usr/share/qgis')

# 로깅 설정
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# 좌표계 설정
DEFAULT_CRS = os.getenv('DEFAULT_CRS', 'EPSG:5186')  # Korea 2000 / Central Belt
OUTPUT_CRS = os.getenv('OUTPUT_CRS', 'EPSG:4326')     # WGS84

# 인코딩 설정
DBF_ENCODING = os.getenv('DBF_ENCODING', 'cp949')

# 스타일 색상 설정
COLOR_GREEN = os.getenv('COLOR_GREEN', '#00FF00')
COLOR_BLUE = os.getenv('COLOR_BLUE', '#0000FF')
COLOR_RED = os.getenv('COLOR_RED', '#FF0000')

# 카테고리 정의
CATEGORIES = {
    'GREEN': '녹색',
    'BLUE': '파란색',
    'RED': '빨간색'
}

def get_output_path(filename: str) -> Path:
    """출력 파일 경로 생성"""
    return OUTPUT_DIR / filename

def get_data_path(filename: str) -> Path:
    """데이터 파일 경로 생성"""
    return DATA_DIR / filename

def get_input_path(filename: str) -> Path:
    """입력 파일 경로 생성"""
    return INPUT_DIR / filename

def get_script_path(script_name: str) -> Path:
    """스크립트 파일 경로 생성"""
    return PROJECT_ROOT / 'scripts' / script_name

# 설정 출력 함수 (디버깅용)
def print_config():
    """현재 설정을 출력합니다."""
    print("=" * 60)
    print("프로젝트 설정")
    print("=" * 60)
    print(f"프로젝트 루트: {PROJECT_ROOT}")
    print(f"데이터 디렉토리: {DATA_DIR}")
    print(f"입력 디렉토리: {INPUT_DIR}")
    print(f"출력 디렉토리: {OUTPUT_DIR}")
    print(f"기본 좌표계: {DEFAULT_CRS}")
    print(f"출력 좌표계: {OUTPUT_CRS}")
    print(f"DBF 인코딩: {DBF_ENCODING}")
    print(f"로그 레벨: {LOG_LEVEL}")
    print("=" * 60)

if __name__ == "__main__":
    print_config()
