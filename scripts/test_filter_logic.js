#!/usr/bin/env node
/**
 * 필터 로직 자동화 테스트
 * Level 3: 로직 검증 (Unit Testing)
 */

const fs = require('fs');
const path = require('path');

// GeoJSON 데이터 로드
const geojsonPath = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/webmap/apartments_with_prices.geojson';
const geojsonData = JSON.parse(fs.readFileSync(geojsonPath, 'utf-8'));
const allApartments = geojsonData.features;

console.log('='.repeat(80));
console.log('필터 로직 자동화 테스트 (Level 3: 로직 검증)');
console.log('='.repeat(80));
console.log();

// DEBUG: Check data immediately after loading
console.log('[DEBUG] Raw GeoJSON features length:', geojsonData.features.length);
console.log('[DEBUG] allApartments length:', allApartments.length);
const debugDongCounts = {};
allApartments.forEach(apt => {
    debugDongCounts[apt.properties.dong] = (debugDongCounts[apt.properties.dong] || 0) + 1;
});
console.log('[DEBUG] 법정동별:', debugDongCounts);
console.log();

console.log(`총 아파트: ${allApartments.length}개`);
console.log();

// ============================================
// 필터 함수 구현 (index.html에서 추출)
// ============================================

function applyFilters(apartments, filterState) {
    return apartments.filter(function(apt) {
        var props = apt.properties;

        // 법정동 필터
        if (filterState.dong.length > 0) {
            if (!filterState.dong.includes(props.dong)) return false;
        }

        // 아파트 이름 검색
        if (filterState.apt_nm) {
            if (!props.apt_nm.includes(filterState.apt_nm)) return false;
        }

        // 평균가 범위 필터 (실거래가 있는 아파트만)
        if (props.avg_price) {
            if (props.avg_price < filterState.avg_price[0] ||
                props.avg_price > filterState.avg_price[1]) return false;
        } else {
            // 평균가 필터가 기본값이 아니면 실거래가 없는 아파트 제외
            if (filterState.avg_price[0] > 28000 || filterState.avg_price[1] < 622833) {
                return false;
            }
        }

        // 평당가 범위 필터 (실거래가 있는 아파트만)
        if (props.price_per_pyeong) {
            var pyeongPrice = props.price_per_pyeong / 10000; // 만원 단위 변환
            if (pyeongPrice < filterState.price_per_pyeong[0] ||
                pyeongPrice > filterState.price_per_pyeong[1]) return false;
        } else {
            // 평당가 필터가 기본값이 아니면 실거래가 없는 아파트 제외
            if (filterState.price_per_pyeong[0] > 2761 || filterState.price_per_pyeong[1] < 19930) {
                return false;
            }
        }

        // 거래건수 범위 필터
        var txCount = props.transaction_count || 0;
        if (txCount < filterState.transaction_count[0] ||
            txCount > filterState.transaction_count[1]) return false;

        // 실거래가 있는 아파트만 체크박스
        if (filterState.has_transactions && !props.transaction_count) return false;

        return true;
    });
}

// ============================================
// 테스트 시나리오
// ============================================

const testScenarios = [
    {
        name: "필터 없음 (기본 상태)",
        filterState: {
            apt_nm: '',
            dong: [],
            avg_price: [28000, 622833],
            price_per_pyeong: [2761, 19930],  // floor(2761.5688), ceil(19929.x)
            transaction_count: [0, 27],
            has_transactions: false
        },
        expected: 814
    },
    {
        name: "법정동: 반포동",
        filterState: {
            apt_nm: '',
            dong: ['반포동'],
            avg_price: [28000, 622833],
            price_per_pyeong: [2761, 19930],
            transaction_count: [0, 27],
            has_transactions: false
        },
        expected: 6
    },
    {
        name: "법정동: 방배동",
        filterState: {
            apt_nm: '',
            dong: ['방배동'],
            avg_price: [28000, 622833],
            price_per_pyeong: [2761, 19930],
            transaction_count: [0, 27],
            has_transactions: false
        },
        expected: 369
    },
    {
        name: "법정동: 서초동",
        filterState: {
            apt_nm: '',
            dong: ['서초동'],
            avg_price: [28000, 622833],
            price_per_pyeong: [2761, 19930],
            transaction_count: [0, 27],
            has_transactions: false
        },
        expected: 437
    },
    {
        name: "법정동: 잠원동",
        filterState: {
            apt_nm: '',
            dong: ['잠원동'],
            avg_price: [28000, 622833],
            price_per_pyeong: [2761, 19930],
            transaction_count: [0, 27],
            has_transactions: false
        },
        expected: 2
    },
    {
        name: "실거래가 있는 아파트만",
        filterState: {
            apt_nm: '',
            dong: [],
            avg_price: [28000, 622833],
            price_per_pyeong: [2761, 19930],
            transaction_count: [0, 27],
            has_transactions: true
        },
        expected: 271
    },
    {
        name: "평균가 100,000~200,000만원",
        filterState: {
            apt_nm: '',
            dong: [],
            avg_price: [100000, 200000],
            price_per_pyeong: [2761, 19930],
            transaction_count: [0, 27],
            has_transactions: false
        },
        expected: 113
    },
    {
        name: "평균가 200,000~300,000만원",
        filterState: {
            apt_nm: '',
            dong: [],
            avg_price: [200000, 300000],
            price_per_pyeong: [2761, 19930],
            transaction_count: [0, 27],
            has_transactions: false
        },
        expected: 106
    },
    {
        name: "평균가 300,000~622,833만원",
        filterState: {
            apt_nm: '',
            dong: [],
            avg_price: [300000, 622833],
            price_per_pyeong: [2761, 19930],
            transaction_count: [0, 27],
            has_transactions: false
        },
        expected: 35
    },
    {
        name: "반포동 + 평균가 100,000만원 이상",
        filterState: {
            apt_nm: '',
            dong: ['반포동'],
            avg_price: [100000, 622833],
            price_per_pyeong: [2761, 19930],
            transaction_count: [0, 27],
            has_transactions: false
        },
        expected: 5
    },
    {
        name: "반포동 + 실거래가 있는 아파트만",
        filterState: {
            apt_nm: '',
            dong: ['반포동'],
            avg_price: [28000, 622833],
            price_per_pyeong: [2761, 19930],
            transaction_count: [0, 27],
            has_transactions: true
        },
        expected: 5
    },
    {
        name: "서초동 + 평균가 200,000만원 이상 + 실거래가 있음",
        filterState: {
            apt_nm: '',
            dong: ['서초동'],
            avg_price: [200000, 622833],
            price_per_pyeong: [2761, 19930],
            transaction_count: [0, 27],
            has_transactions: true
        },
        expected: 100
    },
    {
        name: "아파트 이름: 래미안",
        filterState: {
            apt_nm: '래미안',
            dong: [],
            avg_price: [28000, 622833],
            price_per_pyeong: [2761, 19930],
            transaction_count: [0, 27],
            has_transactions: false
        },
        expected: 22
    },
    {
        name: "아파트 이름: 아크로",
        filterState: {
            apt_nm: '아크로',
            dong: [],
            avg_price: [28000, 622833],
            price_per_pyeong: [2761, 19930],
            transaction_count: [0, 27],
            has_transactions: false
        },
        expected: 5
    },
    {
        name: "아파트 이름: 자이",
        filterState: {
            apt_nm: '자이',
            dong: [],
            avg_price: [28000, 622833],
            price_per_pyeong: [2761, 19930],
            transaction_count: [0, 27],
            has_transactions: false
        },
        expected: 11
    },
    {
        name: "아파트 이름: 푸르지오",
        filterState: {
            apt_nm: '푸르지오',
            dong: [],
            avg_price: [28000, 622833],
            price_per_pyeong: [2761, 19930],
            transaction_count: [0, 27],
            has_transactions: false
        },
        expected: 3
    }
];

// ============================================
// 테스트 실행
// ============================================

console.log('📋 테스트 시나리오 실행 중...');
console.log();

let passed = 0;
let failed = 0;
const failures = [];

testScenarios.forEach((scenario, index) => {
    const filtered = applyFilters(allApartments, scenario.filterState);
    const actual = filtered.length;
    const expected = scenario.expected;
    const isPass = actual === expected;

    if (isPass) {
        console.log(`✅ [${index + 1}/${testScenarios.length}] ${scenario.name}`);
        console.log(`   예상: ${expected}개 | 실제: ${actual}개`);
        passed++;
    } else {
        console.log(`❌ [${index + 1}/${testScenarios.length}] ${scenario.name}`);
        console.log(`   예상: ${expected}개 | 실제: ${actual}개 | 차이: ${actual - expected}개`);
        failed++;
        failures.push({
            name: scenario.name,
            expected,
            actual,
            diff: actual - expected
        });
    }
    console.log();
});

// ============================================
// 결과 요약
// ============================================

console.log('='.repeat(80));
console.log('테스트 결과 요약');
console.log('='.repeat(80));
console.log();

console.log(`총 테스트: ${testScenarios.length}개`);
console.log(`✅ 통과: ${passed}개 (${(passed/testScenarios.length*100).toFixed(1)}%)`);
console.log(`❌ 실패: ${failed}개 (${(failed/testScenarios.length*100).toFixed(1)}%)`);
console.log();

if (failed > 0) {
    console.log('실패한 테스트 상세:');
    failures.forEach((failure, i) => {
        console.log(`${i + 1}. ${failure.name}`);
        console.log(`   예상: ${failure.expected}개 | 실제: ${failure.actual}개 | 차이: ${failure.diff >= 0 ? '+' : ''}${failure.diff}개`);
    });
    console.log();
    process.exit(1);
} else {
    console.log('🎉 모든 테스트 통과!');
    console.log();
    console.log('✅ 필터 로직이 100% 정확하게 작동합니다!');
    process.exit(0);
}
