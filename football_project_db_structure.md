# ⚽ 축구 프로젝트 DB 설계 구조

현재 프로젝트는 PostgreSQL을 사용하며, **총 3개의 테이블**로 구성합니다.

API에서 가져올 수 있는 축구 데이터는 DB에 별도로 저장하지 않고, 사용자 정보와 예측 및 포인트 데이터만 DB에 저장하는 방식입니다.

## 1. DB 테이블 구성

### ① `users` — 회원 정보

회원가입, 로그인, 마이팀 정보를 저장합니다.

| 컬럼 | 설명 |
|---|---|
| `user_id` (PK) | 사용자 고유 번호 |
| `username` | 로그인 아이디 |
| `nickname` | 사용자 닉네임 |
| `password_hash` | 해시 처리된 비밀번호 |
| `my_team_external_id` | Goal API 팀 ID |
| `created_at` | 가입 일시 |

### ② `predictions` — 경기 예측 정보

사용자가 예측한 경기와 실제 경기 결과를 저장합니다.

| 컬럼 | 설명 |
|---|---|
| `prediction_id` (PK) | 예측 고유 번호 |
| `user_id` (FK) | 예측한 사용자 번호 |
| `match_external_id` | Goal API 경기 ID |
| `league_external_id` | Goal API 리그 ID |
| `home_team_name` | 홈팀 이름 |
| `away_team_name` | 원정팀 이름 |
| `match_datetime` | 경기 시작 시간 |
| `season` | 시즌 정보 |
| `predicted_result` | 사용자 예측 결과 |
| `actual_result` | 실제 경기 결과 |
| `is_correct` | 예측 정답 여부 |
| `points_earned` | 해당 예측 획득 포인트 |
| `is_settled` | 정산 완료 여부 |
| `settled_at` | 정산 일시 |
| `created_at` | 예측 등록 일시 |

승·무·패 저장값:

- `HOME_WIN`: 홈팀 승리
- `DRAW`: 무승부
- `AWAY_WIN`: 원정팀 승리

### ③ `point_history` — 포인트 내역

예측에 성공하여 실제 지급받은 포인트를 저장합니다.

| 컬럼 | 설명 |
|---|---|
| `point_id` (PK) | 포인트 기록 고유 번호 |
| `user_id` (FK) | 포인트를 받은 사용자 |
| `prediction_id` (FK) | 포인트를 받은 예측 ID |
| `amount` | 지급 포인트 |
| `reason` | 지급 사유 |
| `created_at` | 지급 일시 |

> 예측 실패 시 포인트는 지급하지 않습니다. 현재 설계에는 포인트 차감 기능이 포함되어 있지 않습니다.

## 2. 테이블 관계

```text
users
  │
  │ user_id (1:N)
  ▼
predictions
  │
  │ prediction_id (1:0..1)
  ▼
point_history
```

- `users.user_id`와 `predictions.user_id`를 연결합니다.
- `predictions.prediction_id`와 `point_history.prediction_id`를 연결합니다.
- 한 사용자는 여러 경기를 예측할 수 있습니다.
- 하나의 예측에 대한 포인트는 중복 지급되지 않도록 `UNIQUE` 제약을 적용합니다.

## 3. API와 DB 역할 구분

### Goal API에서 직접 조회하는 데이터

- 리그 순위
- 팀 정보 및 로고
- 선수 정보
- 경기 일정 및 결과
- 실시간 경기 정보
- 라인업 및 경기 이벤트
- 뉴스 및 영상

### PostgreSQL에 저장하는 데이터

- 회원 정보
- 마이팀 선택 정보
- 사용자 경기 예측
- 실제 결과 및 정산 상태
- 포인트 지급 내역

API 데이터를 전부 DB에 저장하지 않아 불필요한 데이터 누적을 줄입니다.

## 4. 경기 예측 및 포인트 지급 흐름

1. Goal API에서 예정 경기 목록을 조회합니다.
2. 사용자가 경기별 승·무·패를 선택합니다.
3. `predictions` 테이블에 예측 정보를 저장합니다.
4. 경기 시작 후에는 신규 예측 및 수정을 제한합니다.
5. 경기가 종료되면 API에서 실제 결과를 조회합니다.
6. 사용자 예측과 실제 결과를 비교합니다.
7. 적중하면 10포인트를 지급합니다.
8. `point_history`에 지급 내역을 저장합니다.
9. 정산 완료 상태로 변경합니다.
10. `point_history`의 포인트 합계로 랭킹을 계산합니다.

## 5. SQL 파일 구성

```text
project2/
│
├── db.py
│
└── sql/
    ├── create_users.sql
    ├── create_predictions.sql
    ├── create_point_history.sql
    └── create_indexes.sql
```

| 파일 | 역할 |
|---|---|
| `create_users.sql` | 회원 테이블 생성 |
| `create_predictions.sql` | 예측 테이블 생성 |
| `create_point_history.sql` | 포인트 테이블 생성 |
| `create_indexes.sql` | 조회 성능 향상을 위한 인덱스 생성 |

## 6. 최종 설계 방향

**API 데이터는 API에서 조회하고, 우리 서비스에서 관리해야 하는 사용자 정보·예측 정보·포인트 내역만 PostgreSQL에 저장합니다.**

이 구조를 기준으로 DB 기능을 개발합니다.
