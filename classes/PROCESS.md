# Classes 앱 프로세스 설명서

> `/classes/` — 수업 개설 · 수강 신청 · 월별 관리 · 엑셀 다운로드

---

## 1. 전체 흐름 한눈에 보기

```
[수업 개설]
    ↓
[학생을 수업에 등록] ← 한 번만 설정, 변경 전까지 유지
    ↓
[매달 반복: 월별 수강 신청 생성]
    ↓
[관리자 확인 · 수정]
    ↓
[일괄 확정]
    ↓
[엑셀 다운로드]
```

---

## 2. 핵심 개념 (모델)

| 모델 | 역할 | 비유 |
|------|------|------|
| **Lesson** | 수업 정보 (이름, 선생님, 시간표, 기본 수강료) | 수업 카드 |
| **LessonSchedule** | 수업별 요일·시간 (1수업 = 여러 요일 가능) | 시간표 |
| **Enrollment** | "이 학생은 이 수업 수강 중" — 변경 전까지 유효 | 수강 신청서 원본 |
| **MonthlyEnrollment** | 특정 월의 수강 현황 스냅샷 (상태: 신청 중/확정/취소) | 월별 청구 명세 |
| **TuitionPayment** | 수강료 납부 기록 | 영수증 |

### 모델 관계도

```
Lesson ──────────────────────── LessonSchedule (요일/시간)
  │
  ├── Enrollment (학생 ↔ 수업)
  │       └── TuitionPayment (납부 기록)
  │
  └── MonthlyEnrollment (년·월별 수강 현황)
            학생, 수업, 연도, 월, 상태, 수강료
```

---

## 3. 단계별 프로세스

### STEP 1 — 수업 개설
**URL**: `/classes/create/`

수업을 처음 만들 때 입력하는 항목:
- 수업 이름, 과목, 담당 선생님
- 기본 수강료
- 요일별 시간표 (예: 월·수·금 20:00~22:00)

한 번 만들면 `Lesson`에 저장되고, 이후 수정 전까지 유지됩니다.

---

### STEP 2 — 학생 수강 등록
**URL**: `/classes/<수업 pk>/enroll/`

수업 상세 페이지에서 "수강 신청" 버튼으로 진입.
학년별로 학생 목록이 표시되며 체크박스로 다중 선택 가능.

입력 항목:
| 항목 | 설명 |
|------|------|
| 수강 시작일 | 등록일 |
| 수강 종료일 | 비워두면 무기한 수강 |
| 수강료 조정액 | 할인(-) 또는 추가(+) 금액 |

→ `Enrollment` 레코드 생성. **퇴원하거나 수동으로 취소하기 전까지 계속 유효**.

---

### STEP 3 — 매달 월별 수강 신청 생성
**URL**: `/classes/monthly/create/`

**이 단계가 핵심입니다.**

`Enrollment`(수강 등록 원본)에서 해당 월에 활성인 학생을 읽어
`MonthlyEnrollment`(월별 스냅샷)을 일괄 생성합니다.

```
활성 Enrollment 목록
    → 선택 (체크박스)
    → 생성 버튼 클릭
    → MonthlyEnrollment 생성 (상태: '신청 중')
```

- 이미 해당 월에 존재하는 항목은 건너뜁니다 (중복 생성 없음).
- 수강료는 Enrollment의 기본 수강료 기준으로 자동 설정됩니다.
- 기본으로 **다음 달**이 선택되어 있습니다 (← 버튼으로 월 변경 가능).

---

### STEP 4 — 관리자 확인 및 수정
**URL**: `/classes/monthly/`

생성된 MonthlyEnrollment 목록을 수업별로 확인.

**수정 가능한 항목**:
- 수업 변경 (다른 수업으로 이동)
- 상태 변경 (신청 중 / 확정 / 취소)
- 수강료 조정액
- 메모

**상태 종류**:
| 상태 | 의미 |
|------|------|
| 🟡 신청 중 (pending) | 생성 직후 기본 상태 |
| 🟢 확정 (confirmed) | 관리자가 확정 처리 |
| 🔴 취소 (cancelled) | 해당 월 수강 취소 |

---

### STEP 5 — 일괄 확정
**URL**: `/classes/monthly/` (목록 페이지 내 버튼)

체크박스로 항목을 선택하고 "일괄 확정" 버튼 클릭.
상태가 `pending` → `confirmed`으로 변경됩니다.

---

### STEP 6 — 엑셀 다운로드
**URL**: `/classes/monthly/export/?year=YYYY&month=MM`

월별 수강 신청 목록 페이지의 "엑셀 다운로드" 버튼 클릭.

파일 컬럼:
| 컬럼 | 내용 |
|------|------|
| 이름 | 학생 이름 |
| 부모 전화번호 | 부모님 연락처 |
| 청구금액 | 기본 수강료 + 조정액 |
| 내용 | 수업명 |
| 메모 | 메모 |

- 상태 필터(전체/신청 중/확정/취소)가 다운로드에 그대로 반영됩니다.
- 파일명 예: `2026년5월_수강신청_확정.xlsx`

---

## 4. URL 전체 목록

| URL | 기능 |
|-----|------|
| `/classes/` | 수업 목록 + 시간표 보기 |
| `/classes/create/` | 수업 개설 |
| `/classes/<pk>/` | 수업 상세 (수강생 목록, 납부 현황) |
| `/classes/<pk>/edit/` | 수업 수정 |
| `/classes/<pk>/delete/` | 수업 삭제 |
| `/classes/<pk>/enroll/` | 학생 수강 등록 |
| `/classes/<pk>/enrollment/<epk>/edit/` | 수강 정보 수정 |
| `/classes/<pk>/enrollment/<epk>/delete/` | 수강 취소 |
| `/classes/enrollment/<epk>/payment/create/` | 수강료 납부 기록 |
| `/classes/monthly/` | 월별 수강 신청 목록 |
| `/classes/monthly/create/` | 월별 수강 신청 일괄 생성 |
| `/classes/monthly/export/` | 엑셀 다운로드 |
| `/classes/monthly/bulk-confirm/` | 선택 항목 일괄 확정 |
| `/classes/monthly/bulk-delete/` | 선택 항목 일괄 삭제 |
| `/classes/monthly/<pk>/edit/` | 개별 수강 신청 수정 |
| `/classes/monthly/<pk>/delete/` | 개별 수강 신청 삭제 |

---

## 5. Enrollment vs MonthlyEnrollment 차이

| | Enrollment | MonthlyEnrollment |
|-|------------|-------------------|
| 생성 시점 | 학생이 수업에 처음 등록할 때 | 매달 STEP 3에서 생성 |
| 역할 | "이 학생이 이 수업을 듣는다"는 원본 기록 | 특정 월의 청구 명세 |
| 삭제 시점 | 퇴원하거나 수강 취소할 때 | 언제든 삭제/취소 가능 |
| 수량 | 학생당 수업당 1개 | 학생·수업·월 조합으로 1개 |

**핵심**: `Enrollment`가 없으면 `MonthlyEnrollment`를 만들 수 없습니다.
`MonthlyEnrollment`는 `Enrollment`를 읽어서 그 달의 청구 데이터를 만드는 것입니다.

---

## 6. 월별 반복 작업 요약

매달 해야 할 작업:

```
1. /classes/monthly/create/ 접속
2. 대상 월 확인 (기본: 다음 달)
3. 생성 버튼 클릭
4. /classes/monthly/ 에서 목록 확인
5. 필요한 항목 수정 (수업 변경, 금액 조정 등)
6. 전체 선택 → 일괄 확정
7. 엑셀 다운로드
```
