# Tham Chiếu Quy Trình Claude Code (Bản Chuẩn)

## Mục lục
1. Mô hình phát triển
2. Vai trò agent
3. Giai đoạn Requirement
4. Giai đoạn Design
5. Giai đoạn Implementation & Test
6. Quản lý trạng thái dự án
7. Logging giao tiếp giữa agents
8. Nguyên tắc vận hành
9. Workflow mẫu

## Mô hình phát triển
- Dùng mô hình thác nước rút gọn với 4 giai đoạn: `Requirement -> Design -> Implementation -> Test`.
- Main agent điều phối toàn bộ tiến trình và quản lý trạng thái dự án.
- Không chuyển pha khi checkpoint của pha hiện tại chưa được user xác nhận.

## Vai trò agent
- `main`: điều phối, tổng hợp, cập nhật trạng thái.
- `agent-ba`: phân tích yêu cầu, thiết kế hệ thống, hỗ trợ business rules.
- `agent-uiux`: thiết kế trải nghiệm, mô tả screen, dựng UI layer.
- `agent-react`: triển khai business logic, state, API, error handling.

## Giai đoạn Requirement
### Mục tiêu
- Tạo `PRD.md` đầy đủ, có thể dùng làm đầu vào cho Design.

### Thao tác chuẩn
1. Main nhận ý tưởng từ user.
2. Main giao `agent-ba` phân tích yêu cầu.
3. `agent-ba` làm rõ:
- User stories.
- Acceptance criteria.
- Yêu cầu phi chức năng: performance, security, scalability.
- Edge cases, giả định, ràng buộc.
4. `agent-ba` ưu tiên tính năng theo MoSCoW.
5. `agent-ba` xuất file `PRD.md`.

### Cấu trúc tối thiểu của PRD
- Executive Summary.
- Feature Table (đánh số + phụ thuộc giữa tính năng).
- Acceptance Criteria.
- Non-functional Requirements.
- Assumptions & Constraints.

### Checkpoint
- User xác nhận `PRD.md`.
- Main cập nhật trạng thái: `Requirement ✓ -> Design`.

## Giai đoạn Design
### Mục tiêu
- Thiết kế DB, flows, kiến trúc (nếu cần), và mô tả màn hình.

### 2.1 System & Flow Design (agent-ba)
1. Thiết kế database:
- ERD bằng Mermaid.
- Table schema: fields, data types, constraints, relationships.
- Index strategy.
- Lưu tại `design/database/schema.md`.
2. Viết activity diagrams cho từng tính năng:
- User interactions.
- Main flow, decision points, parallel paths.
- Error handling flow.
- Lưu tại `design/flows/[feature-number]-[short-name].md`.
3. Nếu cần, bổ sung system architecture:
- Component diagram.
- API endpoint design.
- State management strategy.

### 2.2 Screen Descriptions (agent-uiux)
- Chỉ bắt đầu sau khi activity diagrams hoàn tất.
- Input: `PRD.md`, toàn bộ files trong `design/flows/`, và design references nếu có.
- Output: `design/screens.md` với mỗi screen gồm:
1. Mục đích.
2. Các thành phần chính (mô tả, tương tác, hiệu ứng).
3. Navigation (đến từ đâu, đi tới đâu).
4. Ghi chú UX và edge cases hiển thị.

### Checkpoint
- User xác nhận `design/database/schema.md` và activity diagrams.
- User xác nhận `design/screens.md`.
- Main cập nhật trạng thái: `Design ✓ -> Implementation`.

## Giai đoạn Implementation & Test
### Mục tiêu
- Triển khai từng tính năng theo thứ tự ưu tiên + phụ thuộc.

### Chu kỳ chuẩn cho mỗi tính năng
1. Chọn tính năng:
- Theo thứ tự Must -> Should -> Could.
- Tôn trọng dependencies trong PRD.
2. UI/UX phase:
- Main giao `agent-uiux` dựng UI layer.
- `agent-uiux` tập trung presentation, interactions, animations, mock data.
3. Business logic phase:
- `agent-uiux` handoff cho `agent-react`.
- `agent-react` làm việc với `agent-ba` để lấy business rules/validations/edge cases.
- `agent-react` triển khai API integration, state management, validations, error handling.
4. Refinement:
- `agent-react` và `agent-uiux` phối hợp fix vấn đề integration UI-logic.
5. Completion:
- `agent-react` hoàn tất chất lượng code và tối ưu.
- Main tóm tắt: phạm vi đã làm, file thay đổi, cách test.

### Checkpoint theo feature
- User tự test trên device/simulator.
- Nếu lỗi: quay lại vòng fix.
- Khi pass: main đánh dấu `[Feature Name] ✓`.

### Checkpoint cuối
- Khi toàn bộ tính năng hoàn tất: `Implementation ✓ -> Complete`.

## Quản lý trạng thái dự án
- Main duy trì file `PROJECT_STATUS.md`.

### Template trạng thái khuyến nghị
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
- [x] Feature A - Completed
- [ ] Feature B - In progress

### Should Have
- [ ] Feature C - Pending

### Could Have
- [ ] Feature D - Pending

## Last Updated
[Date and time]
```

## Logging giao tiếp giữa agents
- Dùng file `AGENT_COMMUNICATION.log`.
- Mục tiêu: audit trail, debug, review collaboration history.

### Format bắt buộc
```text
[YYYY-MM-DD HH:MM:SS] SENDER -> RECEIVER | REQUEST_BRIEF
```

### Quy tắc bắt buộc log
- Main gọi custom agent.
- Custom agent báo kết quả về main.
- Custom agent gọi custom agent khác.
- Agent yêu cầu thông tin từ agent khác.
- Handoff công việc.
- Báo lỗi/vấn đề cho agent khác.

### Không cần log
- Agent nói chuyện trực tiếp với user.
- Agent đọc/ghi file nội bộ.
- Internal reasoning trong cùng 1 agent.

### Best practices cho REQUEST_BRIEF
- Rõ nghĩa, 1 dòng, ngắn gọn.
- Ưu tiên động từ hành động: Phân tích, Thiết kế, Implement, Fix, Handoff, Yêu cầu, Cung cấp.
- Bao gồm context chính: feature/screen/task.
- Target <= 100 ký tự.

### Lệnh append log chuẩn
```bash
echo "[$(date '+%Y-%m-%d %H:%M:%S')] SENDER -> RECEIVER | REQUEST_BRIEF" >> AGENT_COMMUNICATION.log
```

## Nguyên tắc vận hành
1. Không skip phase nếu không có lý do rõ ràng.
2. Mỗi checkpoint phải có user approval.
3. Ưu tiên collaboration hai chiều thay vì handoff một chiều.
4. Tài liệu hóa đầy đủ artifacts chính.
5. Chấp nhận lặp và tinh chỉnh theo feedback.
6. Ưu tiên chất lượng và maintainability.

## Workflow mẫu
1. User đưa ý tưởng.
2. Requirement:
- Main -> BA phân tích.
- BA + user làm rõ.
- BA tạo PRD.
- User approve.
3. Design:
- Main -> BA thiết kế DB/flows.
- User approve DB/flows.
- Main -> UIUX mô tả screens.
- User approve screens.
4. Implementation:
- Main -> UIUX dựng UI cho từng feature.
- UIUX -> React handoff.
- React <-> BA lấy rules.
- React <-> UIUX refinement.
- User test và approve từng feature.
5. Complete:
- Main cập nhật trạng thái dự án hoàn tất.
