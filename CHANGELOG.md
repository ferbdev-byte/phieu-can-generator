# Changelog

Theo [Keep a Changelog](https://keepachangelog.com/vi/1.1.0/) và [SemVer](https://semver.org/lang/vi/).

## [0.2.0] - 2026-11-23

### Thêm

- Tuỳ chọn `--a4` in phiếu khổ A4 dọc cho máy in văn phòng.
- Đánh dấu `py.typed` (PEP 561): dự án khác dùng thư viện sẽ nhận được thông tin kiểu.

### Cải thiện

- CI kiểm tra kiểu tĩnh bằng mypy ở chế độ strict.
- CI đo độ phủ test (branch coverage), fail nếu dưới 80%.
- GitHub Actions nâng lên bản mới (checkout v7, setup-python v7).

## [0.1.0] - 2026-11-23

### Thêm

- Bản phát hành đầu tiên. Xuất phiếu cân PDF A5 tiếng Việt, đọc số tiền bằng chữ, in cả lô từ weighbridge-reader.
