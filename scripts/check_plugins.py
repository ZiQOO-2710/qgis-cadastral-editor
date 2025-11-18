# QGIS 플러그인 설치 확인 스크립트

from qgis.utils import plugins, pluginMetadata

print("=" * 60)
print("설치된 QGIS 플러그인 목록")
print("=" * 60)

# 모든 설치된 플러그인 확인
installed_plugins = plugins.keys()

if not installed_plugins:
    print("설치된 플러그인이 없습니다.")
else:
    for plugin_name in sorted(installed_plugins):
        try:
            version = pluginMetadata(plugin_name, 'version')
            print(f"✓ {plugin_name} (버전: {version})")
        except:
            print(f"✓ {plugin_name}")

print("\n" + "=" * 60)
print("배경지도 플러그인 확인")
print("=" * 60)

# QuickMapServices 확인 (실제 패키지명은 quick_map_services)
if 'quick_map_services' in installed_plugins:
    print("✅ QuickMapServices 플러그인이 설치되어 있습니다!")
    try:
        version = pluginMetadata('quick_map_services', 'version')
        print(f"   버전: {version}")
    except:
        pass
    print("\n사용 방법:")
    print("   메뉴 → 웹 → QuickMapServices → 원하는 배경지도 선택")
    print("   (먼저 '설정'에서 'Get contributed pack' 클릭하면 더 많은 지도 사용 가능)")
else:
    print("❌ QuickMapServices 플러그인이 설치되지 않았습니다.")

# TMS for Korea 확인
if 'tmsforkorea' in installed_plugins:
    print("\n✅ TMS for Korea 플러그인도 설치되어 있습니다!")
    try:
        version = pluginMetadata('tmsforkorea', 'version')
        print(f"   버전: {version}")
    except:
        pass
    print("\n사용 방법:")
    print("   메뉴 → 웹 → TMS for Korea → 원하는 한국 배경지도 선택")
    print("   (브이월드, 다음, 네이버 등 한국 지도 제공)")
else:
    print("\n❌ TMS for Korea 플러그인이 설치되지 않았습니다.")

print("=" * 60)
