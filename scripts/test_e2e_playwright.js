#!/usr/bin/env node
/**
 * Playwright E2E 자동화 테스트
 * Level 4: 통합검증 (Integration Testing)
 *
 * 브라우저에서 실제 웹맵을 열고 필터 기능을 자동으로 테스트합니다.
 */

const { chromium } = require('playwright');

async function runE2ETests() {
    console.log('='.repeat(80));
    console.log('Playwright E2E 자동화 테스트 (Level 4: 통합검증)');
    console.log('='.repeat(80));
    console.log();

    let browser;
    let passed = 0;
    let failed = 0;
    const failures = [];

    try {
        // 1. 브라우저 시작
        console.log('🌐 Chromium 브라우저 시작 중...');
        browser = await chromium.launch({
            headless: true  // headless 모드로 실행
        });
        const context = await browser.newContext({
            viewport: { width: 1920, height: 1080 }
        });
        const page = await context.newPage();

        // 2. 페이지 로드
        console.log('📄 웹페이지 로딩 중: http://localhost:8000/');
        await page.goto('http://localhost:8000/', {
            waitUntil: 'networkidle',
            timeout: 30000
        });

        // 3. 초기 로딩 대기
        console.log('⏳ GeoJSON 데이터 로딩 대기 중...');
        await page.waitForTimeout(3000);  // 데이터 로딩 대기

        // Helper: 통계 값 가져오기
        async function getStatValue() {
            const statText = await page.textContent('#total-apts');
            // 숫자만 추출 (예: "814" or "814개")
            const cleaned = statText.replace(/[^0-9]/g, '');
            return cleaned ? parseInt(cleaned) : 0;
        }

        // Helper: 필터 초기화
        async function resetFilters() {
            const resetBtn = await page.$('button:has-text("모든 필터 초기화")');
            if (resetBtn && await resetBtn.isVisible()) {
                await resetBtn.click();
                await page.waitForTimeout(500);
            }
        }

        console.log();
        console.log('📋 테스트 시나리오 실행 중...');
        console.log();

        // ===== 테스트 1: 기본 상태 =====
        await resetFilters();
        let count = await getStatValue();
        let expected = 814;
        if (count === expected) {
            console.log(`✅ [1/16] 필터 없음 (기본 상태)`);
            console.log(`   예상: ${expected}개 | 실제: ${count}개`);
            passed++;
        } else {
            console.log(`❌ [1/16] 필터 없음 (기본 상태)`);
            console.log(`   예상: ${expected}개 | 실제: ${count}개 | 차이: ${count - expected}개`);
            failed++;
            failures.push({ name: '필터 없음', expected, actual: count });
        }
        console.log();

        // ===== 테스트 2-5: 법정동 필터 =====
        const dongTests = [
            { dong: '반포동', expected: 6 },
            { dong: '방배동', expected: 369 },
            { dong: '서초동', expected: 437 },
            { dong: '잠원동', expected: 2 }
        ];

        for (let i = 0; i < dongTests.length; i++) {
            await resetFilters();
            const { dong, expected } = dongTests[i];

            // 체크박스 클릭
            await page.click(`input[type="checkbox"][value="${dong}"]`);
            await page.waitForTimeout(500);  // 필터 적용 대기

            const count = await getStatValue();
            const testNum = i + 2;

            if (count === expected) {
                console.log(`✅ [${testNum}/16] 법정동: ${dong}`);
                console.log(`   예상: ${expected}개 | 실제: ${count}개`);
                passed++;
            } else {
                console.log(`❌ [${testNum}/16] 법정동: ${dong}`);
                console.log(`   예상: ${expected}개 | 실제: ${count}개 | 차이: ${count - expected}개`);
                failed++;
                failures.push({ name: `법정동: ${dong}`, expected, actual: count });
            }
            console.log();
        }

        // ===== 테스트 6: 실거래가 있는 아파트만 =====
        await resetFilters();
        await page.click('input[type="checkbox"]#filter-has_transactions');
        await page.waitForTimeout(500);

        count = await getStatValue();
        expected = 271;
        if (count === expected) {
            console.log(`✅ [6/16] 실거래가 있는 아파트만`);
            console.log(`   예상: ${expected}개 | 실제: ${count}개`);
            passed++;
        } else {
            console.log(`❌ [6/16] 실거래가 있는 아파트만`);
            console.log(`   예상: ${expected}개 | 실제: ${count}개 | 차이: ${count - expected}개`);
            failed++;
            failures.push({ name: '실거래가 있는 아파트만', expected, actual: count });
        }
        console.log();

        // ===== 테스트 7-9: 평균가 범위 필터 =====
        const priceTests = [
            { min: 100000, max: 200000, expected: 113 },
            { min: 200000, max: 300000, expected: 106 },
            { min: 300000, max: 622833, expected: 35 }
        ];

        for (let i = 0; i < priceTests.length; i++) {
            await resetFilters();
            const { min, max, expected } = priceTests[i];

            // 슬라이더 값 설정 (JavaScript 직접 실행)
            await page.evaluate(({ min, max }) => {
                window.filterState.avg_price = [min, max];
                window.applyFiltersAndRender();
            }, { min, max });
            await page.waitForTimeout(500);

            const count = await getStatValue();
            const testNum = i + 7;

            if (count === expected) {
                console.log(`✅ [${testNum}/16] 평균가 ${min.toLocaleString()}~${max.toLocaleString()}만원`);
                console.log(`   예상: ${expected}개 | 실제: ${count}개`);
                passed++;
            } else {
                console.log(`❌ [${testNum}/16] 평균가 ${min.toLocaleString()}~${max.toLocaleString()}만원`);
                console.log(`   예상: ${expected}개 | 실제: ${count}개 | 차이: ${count - expected}개`);
                failed++;
                failures.push({ name: `평균가 ${min.toLocaleString()}~${max.toLocaleString()}`, expected, actual: count });
            }
            console.log();
        }

        // ===== 테스트 10: 반포동 + 평균가 100,000만원 이상 =====
        await resetFilters();
        await page.click('input[type="checkbox"][value="반포동"]');
        await page.evaluate(() => {
            window.filterState.avg_price = [100000, 622833];
            window.applyFiltersAndRender();
        });
        await page.waitForTimeout(500);

        count = await getStatValue();
        expected = 5;
        if (count === expected) {
            console.log(`✅ [10/16] 반포동 + 평균가 100,000만원 이상`);
            console.log(`   예상: ${expected}개 | 실제: ${count}개`);
            passed++;
        } else {
            console.log(`❌ [10/16] 반포동 + 평균가 100,000만원 이상`);
            console.log(`   예상: ${expected}개 | 실제: ${count}개 | 차이: ${count - expected}개`);
            failed++;
            failures.push({ name: '반포동 + 평균가 100k+', expected, actual: count });
        }
        console.log();

        // ===== 테스트 11: 반포동 + 실거래가 있는 아파트만 =====
        await resetFilters();
        await page.click('input[type="checkbox"][value="반포동"]');
        await page.click('input[type="checkbox"]#filter-has-tx');
        await page.waitForTimeout(500);

        count = await getStatValue();
        expected = 5;
        if (count === expected) {
            console.log(`✅ [11/16] 반포동 + 실거래가 있는 아파트만`);
            console.log(`   예상: ${expected}개 | 실제: ${count}개`);
            passed++;
        } else {
            console.log(`❌ [11/16] 반포동 + 실거래가 있는 아파트만`);
            console.log(`   예상: ${expected}개 | 실제: ${count}개 | 차이: ${count - expected}개`);
            failed++;
            failures.push({ name: '반포동 + 실거래가 있음', expected, actual: count });
        }
        console.log();

        // ===== 테스트 12: 서초동 + 평균가 200,000만원 이상 + 실거래가 있음 =====
        await resetFilters();
        await page.click('input[type="checkbox"][value="서초동"]');
        await page.click('input[type="checkbox"]#filter-has-tx');
        await page.evaluate(() => {
            window.filterState.avg_price = [200000, 622833];
            window.applyFiltersAndRender();
        });
        await page.waitForTimeout(500);

        count = await getStatValue();
        expected = 100;
        if (count === expected) {
            console.log(`✅ [12/16] 서초동 + 평균가 200,000만원 이상 + 실거래가 있음`);
            console.log(`   예상: ${expected}개 | 실제: ${count}개`);
            passed++;
        } else {
            console.log(`❌ [12/16] 서초동 + 평균가 200,000만원 이상 + 실거래가 있음`);
            console.log(`   예상: ${expected}개 | 실제: ${count}개 | 차이: ${count - expected}개`);
            failed++;
            failures.push({ name: '서초동 + 200k+ + 실거래', expected, actual: count });
        }
        console.log();

        // ===== 테스트 13-16: 아파트 이름 검색 =====
        const searchTests = [
            { keyword: '래미안', expected: 22 },
            { keyword: '아크로', expected: 5 },
            { keyword: '자이', expected: 11 },
            { keyword: '푸르지오', expected: 3 }
        ];

        for (let i = 0; i < searchTests.length; i++) {
            await resetFilters();
            const { keyword, expected } = searchTests[i];

            // 검색창에 입력
            await page.fill('input#filter-apt-name', keyword);
            await page.waitForTimeout(800);  // Debounce 대기 (300ms + 여유)

            const count = await getStatValue();
            const testNum = i + 13;

            if (count === expected) {
                console.log(`✅ [${testNum}/16] 아파트 이름: ${keyword}`);
                console.log(`   예상: ${expected}개 | 실제: ${count}개`);
                passed++;
            } else {
                console.log(`❌ [${testNum}/16] 아파트 이름: ${keyword}`);
                console.log(`   예상: ${expected}개 | 실제: ${count}개 | 차이: ${count - expected}개`);
                failed++;
                failures.push({ name: `아파트 이름: ${keyword}`, expected, actual: count });
            }
            console.log();
        }

        // 결과 요약
        console.log('='.repeat(80));
        console.log('테스트 결과 요약');
        console.log('='.repeat(80));
        console.log();
        console.log(`총 테스트: 16개`);
        console.log(`✅ 통과: ${passed}개 (${(passed/16*100).toFixed(1)}%)`);
        console.log(`❌ 실패: ${failed}개 (${(failed/16*100).toFixed(1)}%)`);
        console.log();

        if (failed > 0) {
            console.log('실패한 테스트 상세:');
            failures.forEach((failure, i) => {
                console.log(`${i + 1}. ${failure.name}`);
                console.log(`   예상: ${failure.expected}개 | 실제: ${failure.actual}개 | 차이: ${failure.actual >= failure.expected ? '+' : ''}${failure.actual - failure.expected}개`);
            });
            console.log();
        } else {
            console.log('🎉 모든 테스트 통과!');
            console.log();
            console.log('✅ 웹맵 필터 시스템이 100% 정확하게 작동합니다!');
            console.log('✅ Headless Browser 자동화 테스트 완료!');
        }

    } catch (error) {
        console.error('\n❌ 테스트 실행 중 오류 발생:');
        console.error(error.message);
        console.error(error.stack);
        process.exit(1);
    } finally {
        if (browser) {
            await browser.close();
        }
        process.exit(failed > 0 ? 1 : 0);
    }
}

// 실행
runE2ETests().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});
