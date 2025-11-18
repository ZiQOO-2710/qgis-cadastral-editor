#!/usr/bin/env python3
"""
무릉리 스타일 지적도 자동화 - 빠른 시작 스크립트

사용법:
    python templates/muneung_style/quick_start.py \\
        --name "프로젝트명" \\
        --csv "토지조서.csv 경로" \\
        --shapefile "원본_shapefile 경로" \\
        --pnu "PNU코드" \\
        --display "표시명" \\
        --location "위치"

예시:
    python templates/muneung_style/quick_start.py \\
        --name muneung \\
        --csv "/mnt/c/Users/ksj27/PROJECTS/autooffice/서귀포시 대정읍 무릉리 토지조서.csv" \\
        --shapefile "data/원본_shapefile/서귀포시/LSMD_CONT_LDREG_50130_202510.shp" \\
        --pnu "5013010600" \\
        --display "무릉리 필지 현황" \\
        --location "제주특별자치도 서귀포시 대정읍 무릉리"
"""

import argparse
import csv
import yaml
import shutil
import subprocess
from pathlib import Path

def extract_jibun_from_csv(csv_path):
    """토지조서 CSV에서 지번 추출"""
    jibun_list = []

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            bon = row.get('본번', '').strip()
            bu = row.get('부번', '').strip()

            if bon:
                if bu:
                    jibun = f"{bon}-{bu}"
                else:
                    jibun = bon
                jibun_list.append(jibun)

    return jibun_list

def create_project_config(args, jibun_list):
    """프로젝트 설정 파일 생성"""
    project_dir = Path(f"projects/{args.name}")
    project_dir.mkdir(parents=True, exist_ok=True)

    # 지번 목록 파일 생성
    list_file = Path(f"input/{args.name}_list.txt")
    with open(list_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(jibun_list))

    print(f"✅ 지번 목록 생성: {list_file} ({len(jibun_list)}개)")

    # config.yaml 생성
    config = {
        'project': {
            'name': args.name,
            'display_name': args.display,
            'location': args.location
        },
        'input': {
            'source_shapefile': args.shapefile,
            'pnu_filter': args.pnu,
            'parcel_lists': {
                'green': f"input/{args.name}_list.txt",
                'blue': "input/empty.txt",
                'red': "input/empty.txt"
            }
        },
        'output': {
            'directory': 'output',
            'formats': ['shapefile', 'csv', 'qml', 'webmap']
        },
        'processing': {
            'clean_jibun': True
        },
        'style': {
            'categories': {
                'ALL': {
                    'color': '#FFFF00',
                    'label': f"{args.display.split()[0]} 필지"
                }
            }
        },
        'crs': {
            'source': 'EPSG:5186',
            'target': 'EPSG:4326'
        },
        'encoding': {
            'dbf': 'cp949',
            'csv': 'utf-8'
        }
    }

    config_file = project_dir / 'config.yaml'
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

    print(f"✅ 설정 파일 생성: {config_file}")

    return config_file

def run_automation(config_file):
    """자동화 스크립트 실행"""
    print("\n🚀 자동화 스크립트 실행 중...")

    cmd = [
        'python', 'scripts/cadastral_auto.py',
        '--config', str(config_file)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ 자동화 실패:")
        print(result.stderr)
        return False

    print(result.stdout)
    return True

def customize_webmap(args):
    """웹맵 HTML을 무릉리 스타일로 커스터마이즈"""
    template_path = Path("templates/muneung_style/webmap_template.html")
    output_path = Path("output/webmap/index.html")

    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 플레이스홀더 치환
    html = html.replace('{{DISPLAY_NAME}}', args.display)
    html = html.replace('{{LOCATION}}', args.location)
    html = html.replace('{{CATEGORY_LABEL}}', f"{args.display.split()[0]} 필지")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ 웹맵 커스터마이즈 완료: {output_path}")

def start_http_server():
    """HTTP 서버 시작"""
    import os
    import time

    webmap_dir = Path("output/webmap").absolute()
    os.chdir(webmap_dir)

    print(f"\n🌐 HTTP 서버 시작 중...")
    print(f"📂 디렉토리: {webmap_dir}")
    print(f"🔗 접속 주소: http://localhost:8888/index.html")
    print(f"⏹️  종료: Ctrl+C\n")

    subprocess.run(['python3', '-m', 'http.server', '8888'])

def main():
    parser = argparse.ArgumentParser(description='무릉리 스타일 지적도 자동화')
    parser.add_argument('--name', required=True, help='프로젝트 이름 (예: muneung)')
    parser.add_argument('--csv', required=True, help='토지조서 CSV 파일 경로')
    parser.add_argument('--shapefile', required=True, help='원본 shapefile 경로')
    parser.add_argument('--pnu', required=True, help='PNU 필터 코드 (예: 5013010600)')
    parser.add_argument('--display', required=True, help='표시 이름 (예: 무릉리 필지 현황)')
    parser.add_argument('--location', required=True, help='위치 (예: 제주특별자치도 서귀포시 대정읍 무릉리)')
    parser.add_argument('--no-server', action='store_true', help='HTTP 서버 시작 안함')

    args = parser.parse_args()

    print("=" * 60)
    print("무릉리 스타일 지적도 자동화 시작")
    print("=" * 60)

    # 1. CSV에서 지번 추출
    print("\n[1/5] 토지조서에서 지번 추출 중...")
    jibun_list = extract_jibun_from_csv(args.csv)

    # 2. 프로젝트 설정 생성
    print(f"\n[2/5] 프로젝트 설정 생성 중...")
    config_file = create_project_config(args, jibun_list)

    # 3. 자동화 실행
    print(f"\n[3/5] 자동화 스크립트 실행 중...")
    if not run_automation(config_file):
        print("\n❌ 자동화 실패. 종료합니다.")
        return

    # 4. 웹맵 커스터마이즈
    print(f"\n[4/5] 웹맵 커스터마이즈 중...")
    customize_webmap(args)

    # 5. HTTP 서버 시작
    print(f"\n[5/5] 완료!")
    print("\n" + "=" * 60)
    print("✅ 모든 작업 완료")
    print("=" * 60)

    if not args.no_server:
        start_http_server()

if __name__ == '__main__':
    main()
