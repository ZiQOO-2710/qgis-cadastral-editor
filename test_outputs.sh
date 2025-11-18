#!/bin/bash
echo "📂 출력 파일 검증"
echo "===================="
echo ""

echo "1. Shapefile 확인:"
ls -lh output/jubulli_categorized.* 2>/dev/null | awk '{print "  " $9, "-", $5}'

echo ""
echo "2. CSV 내용 확인 (처음 5줄):"
head -5 output/jubulli_areas.csv 2>/dev/null | sed 's/^/  /'

echo ""
echo "3. GeoJSON 필지 개수:"
if [ -f output/webmap/parcels.geojson ]; then
    count=$(grep -o '"type":"Feature"' output/webmap/parcels.geojson | wc -l)
    echo "  총 $count 개 필지"
fi

echo ""
echo "4. 웹맵 HTML 크기:"
ls -lh output/webmap/index.html 2>/dev/null | awk '{print "  " $5}'

echo ""
echo "5. 카테고리별 필지 확인:"
if [ -f output/jubulli_areas.csv ]; then
    echo "  GREEN:"
    grep ",GREEN," output/jubulli_areas.csv | wc -l | xargs echo "    개수:" 
    echo "  BLUE:"
    grep ",BLUE," output/jubulli_areas.csv | wc -l | xargs echo "    개수:"
    echo "  RED:"
    grep ",RED," output/jubulli_areas.csv | wc -l | xargs echo "    개수:"
fi
