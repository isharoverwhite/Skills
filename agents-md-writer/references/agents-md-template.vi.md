# Quy trình phát triển ứng dụng với Claude Code - {{PROJECT_NAME}}

Tài liệu này mô tả quy trình phát triển ứng dụng theo mô hình thác nước rút gọn với 4 giai đoạn: `Requirement -> Design -> Implementation -> Test`.

## Tổng quan

Dự án dùng 3 custom agents và 1 main agent:
- `{{BA_AGENT}}` (Business Analyst): phân tích yêu cầu và thiết kế hệ thống.
- `{{UIUX_AGENT}}` (UI/UX Designer): thiết kế giao diện và trải nghiệm.
- `{{REACT_AGENT}}` (React Native Developer): triển khai code nghiệp vụ.
- `{{MAIN_AGENT}}` (Main): điều phối workflow và quản lý trạng thái dự án.

---

## Giai đoạn 1: Requirement

### Mục tiêu
Thu thập và tài liệu hóa yêu cầu vào `PRD.md`.

### Quy trình
1. `{{MAIN_AGENT}}` nhận bài toán từ user.
2. `{{MAIN_AGENT}}` gọi `{{BA_AGENT}}` để phân tích:
- Chi tiết yêu cầu.
- Yêu cầu ngầm định và edge cases.
- User stories và acceptance criteria.
- Yêu cầu phi chức năng.
3. `{{BA_AGENT}}` cộng tác với user để làm rõ mơ hồ, giả định, ưu tiên tính năng.
4. `{{BA_AGENT}}` tạo `PRD.md` gồm:
- Executive Summary.
- Feature Table (đánh số + dependencies).
- Acceptance Criteria.
- Non-functional Requirements.
- Assumptions & Constraints.

### Checkpoint
- User xác nhận `PRD.md`.
- `{{MAIN_AGENT}}` cập nhật trạng thái: `Requirement ✓ -> Design`.

---

## Giai đoạn 2: Design

### Mục tiêu
Thiết kế kiến trúc, database, luồng nghiệp vụ và mô tả screens.

### 2.1 System & Flow Design ({{BA_AGENT}})
1. Thiết kế database và lưu `design/database/schema.md`:
- ERD (Mermaid).
- Table schemas.
- Constraints, relationships, index strategy.
2. Viết activity diagrams và lưu `design/flows/[feature-number]-[short-name].md`:
- Luồng nghiệp vụ chính.
- Decision points và nhánh lỗi.
- Parallel processes khi cần.
3. Nếu cần, bổ sung thiết kế kiến trúc:
- Component diagram.
- API endpoints.
- State management strategy.

### 2.2 Screen Descriptions ({{UIUX_AGENT}})
Chỉ bắt đầu sau khi `{{BA_AGENT}}` hoàn tất toàn bộ activity diagrams.

1. `{{MAIN_AGENT}}` gọi `{{UIUX_AGENT}}` với đầu vào:
- `PRD.md`.
- Toàn bộ files trong `design/flows/`.
- Design references (nếu có).
2. `{{UIUX_AGENT}}` tạo `design/screens.md` với từng screen gồm:
- Mục đích.
- Các thành phần chính (mô tả, tương tác, hiệu ứng).
- Navigation vào/ra.
- Ghi chú UX và edge cases hiển thị.

### Checkpoint
- User xác nhận `design/database/schema.md` và activity diagrams.
- User xác nhận `design/screens.md`.
- `{{MAIN_AGENT}}` cập nhật: `Design ✓ -> Implementation`.

---

## Giai đoạn 3: Implementation & Test

### Mục tiêu
Triển khai từng tính năng theo thiết kế và kiểm thử trên thiết bị/simulator.

### Quy trình cho mỗi tính năng
1. Chọn tính năng theo PRD:
- Theo ưu tiên Must -> Should -> Could.
- Tôn trọng dependencies.
2. UI/UX phase:
- `{{MAIN_AGENT}}` giao `{{UIUX_AGENT}}` dựng UI.
- `{{UIUX_AGENT}}` tập trung presentation layer, interactions, animation, mock data.
3. Business logic phase:
- `{{UIUX_AGENT}}` handoff cho `{{REACT_AGENT}}`.
- `{{REACT_AGENT}}` phối hợp `{{BA_AGENT}}` để lấy rules và edge cases.
- `{{REACT_AGENT}}` triển khai state, API integration, validation, error handling.
4. Refinement:
- `{{REACT_AGENT}}` và `{{UIUX_AGENT}}` xử lý vấn đề integration UI-logic.
5. Completion:
- `{{REACT_AGENT}}` hoàn tất code quality/performance.
- `{{MAIN_AGENT}}` tóm tắt phạm vi, file thay đổi, hướng dẫn test.

### Checkpoint theo feature
- User test và phản hồi.
- Nếu lỗi: quay lại fix.
- Nếu pass: cập nhật `[Feature Name] ✓`.

### Checkpoint toàn dự án
- Hoàn thành toàn bộ features: `Implementation ✓ -> Complete`.

---

## Quản lý trạng thái dự án

Main agent duy trì file `{{STATUS_FILE}}`.

```markdown
# Project Status

## Current Phase: [Requirement|Design|Implementation|Complete]

## Progress

### ✓ Completed Phases
- [x] Requirement - PRD confirmed on [date]
- [x] Design - System design confirmed on [date]

### -> Current Phase
- [ ] Implementation - In progress

## Features Status

### Must Have
- [ ] Feature A - Pending

### Should Have
- [ ] Feature B - Pending

### Could Have
- [ ] Feature C - Pending

## Last Updated
[Date and time]
```

---

## Agent Communication Logging

### Mục đích
Theo dõi toàn bộ giao tiếp giữa agents để audit, debug và review collaboration.

### File log
- `{{COMM_LOG_FILE}}`

### Format log
```text
[YYYY-MM-DD HH:MM:SS] SENDER -> RECEIVER | REQUEST_BRIEF
```

### Trường hợp bắt buộc log
- Main gọi custom agent.
- Custom agent báo cáo kết quả cho main.
- Custom agent gọi custom agent khác.
- Agent yêu cầu dữ liệu/thông tin từ agent khác.
- Handoff công việc.
- Báo lỗi/vấn đề giữa agents.

### Trường hợp không cần log
- Agent tương tác trực tiếp với user.
- Agent đọc/ghi file nội bộ.
- Internal reasoning của một agent.

### Cách append log
```bash
echo "[$(date '+%Y-%m-%d %H:%M:%S')] SENDER -> RECEIVER | REQUEST_BRIEF" >> {{COMM_LOG_FILE}}
```

### Quy ước REQUEST_BRIEF
- Ngắn gọn, rõ nghĩa, 1 dòng.
- Tối đa 100 ký tự (khuyến nghị).
- Dùng động từ hành động và có context feature/screen/task.

---

## Vai trò và trách nhiệm

### {{MAIN_AGENT}} (Main Agent)
- Điều phối workflow giữa các agents.
- Quản lý trạng thái dự án.
- Tổng hợp kết quả và báo cáo cho user.
- Đảm bảo checkpoint được approve trước khi qua pha tiếp theo.

### {{BA_AGENT}} (Business Analyst)
- Requirement: tạo PRD, làm rõ yêu cầu.
- Design: DB schema, activity diagrams, kiến trúc.
- Implementation: cung cấp business rules cho `{{REACT_AGENT}}`.

### {{UIUX_AGENT}} (UI/UX Designer)
- Design: mô tả screens (`design/screens.md`).
- Implementation: code UI layer và interactions.
- Phối hợp `{{REACT_AGENT}}` để refine integration.

### {{REACT_AGENT}} (React Native Developer)
- Implementation: business logic, API, state, validation.
- Kết hợp `{{UIUX_AGENT}}` để đảm bảo UI tương thích nghiệp vụ.
- Xử lý edge cases và error flows.

---

## Nguyên tắc làm việc
1. Không skip phase khi chưa có lý do rõ ràng.
2. Mỗi checkpoint cần user approval.
3. Ưu tiên collaboration hơn handoff một chiều.
4. Lưu đầy đủ artifacts vào file.
5. Chấp nhận iterate theo feedback.
6. Ưu tiên chất lượng và maintainability.

---

## Workflow mẫu

1. User nêu ý tưởng.
2. Requirement:
- `{{MAIN_AGENT}} -> {{BA_AGENT}}`: phân tích.
- `{{BA_AGENT}} <-> user`: làm rõ.
- `{{BA_AGENT}}`: tạo `PRD.md`.
- User approve.
3. Design:
- `{{MAIN_AGENT}} -> {{BA_AGENT}}`: DB + flows.
- User approve DB/flows.
- `{{MAIN_AGENT}} -> {{UIUX_AGENT}}`: mô tả screens.
- User approve `design/screens.md`.
4. Implementation:
- `{{MAIN_AGENT}} -> {{UIUX_AGENT}}`: dựng UI theo feature.
- `{{UIUX_AGENT}} -> {{REACT_AGENT}}`: handoff UI.
- `{{REACT_AGENT}} <-> {{BA_AGENT}}`: xác nhận rules.
- `{{REACT_AGENT}} <-> {{UIUX_AGENT}}`: refinement.
- User test từng feature.
5. Complete:
- `{{MAIN_AGENT}}` cập nhật trạng thái dự án hoàn tất.
