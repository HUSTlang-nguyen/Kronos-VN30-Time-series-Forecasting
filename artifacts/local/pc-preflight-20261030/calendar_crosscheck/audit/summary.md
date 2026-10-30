# Kiểm toán dữ liệu VN30

Trạng thái: **unverified**. 2271 phiên; SHA256 `fee0bd8c240a9d2be4ef5c9d287eede6c5506b0358c25545e72de99709da4fd2`.

Raw/timestamp/flags replay: pass. Open bằng Close trước: 78 phiên. Ngoài request: 1. Sai khác OHLC chưa giải quyết: 1230.

Đối chiếu lịch: pass. Ngày kiểm tra bắt buộc chưa có nguồn độc lập: 0.

Không sửa giá. Không xác nhận chất lượng thị trường chỉ từ checksum.

| Nguồn đối chiếu | Trường | Số chênh lệch | Lớn nhất (điểm) |
|---|---|---:|---:|
| dnse | close | 54 | 16.35 |
| dnse | high | 114 | 36.81 |
| dnse | low | 237 | 34.96 |
| dnse | open | 448 | 47.91 |
| vps | close | 6 | 2.47 |
| vps | high | 55 | 36.81 |
| vps | low | 169 | 34.96 |
| vps | open | 147 | 27.96 |

Chênh lệch giữa nhà cung cấp chưa xác định được bên nào sai. Không được xem số đếm này là số lỗi đã chứng minh của VNDIRECT.

Bước giải quyết: đối chiếu giá công bố có nguồn cho các ngày cụ thể, xác minh cách dựng O/H/L và hoàn tất lịch phiên. Nếu chưa có bằng chứng, giữ trạng thái chưa kiểm chứng và chặn huấn luyện chính.
