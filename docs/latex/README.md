# Báo cáo LaTeX VN30

Báo cáo của nhóm **1nsider**, Vi Nguyễn Ngọc Châu và Nguyễn Hoàng Kiên.

- `VN30_Report.pdf`: bản đọc và in A4.
- `VN30_LaTeX_Source.zip`: source độc lập, có đủ bảng, hình vector và bibliography.
- `main.tex`: nội dung chính; `references.bib`: tài liệu tham khảo.

## Sửa trên Overleaf

Tạo project bằng **Upload Project**, chọn ZIP source và đặt compiler thành
**XeLaTeX**, main document là `main.tex`. Không chọn pdfLaTeX vì tài liệu dùng
Unicode tiếng Việt và `fontspec`. Hình và bảng đã có sẵn; không cần Python,
dataset, checkpoint hoặc GPU để biên dịch. Source dùng Times New Roman/Arial
nếu có, nếu không tự dùng TeX Gyre Termes/Heros. Đổi font có thể làm thay đổi
ngắt trang so với bản PDF đính kèm.

## Biên dịch local

Có thể dùng Tectonic 0.17.0 (đã dùng để dựng PDF kèm theo):

```powershell
./compile.ps1
# Nếu Tectonic chưa nằm trong PATH:
./compile.ps1 -Tectonic 'C:/duong-dan/tectonic.exe'
```

Script dùng thư mục `.build/`, lưu PDF cuối ở `VN30_Report.pdf` và dừng nếu
biên dịch lỗi. Lần chạy đầu Tectonic cần mạng để lấy các package LaTeX.
Không có script tự cài chương trình hoặc dịch vụ trả phí.

Với TeX Live/MiKTeX có XeLaTeX và BibTeX, chạy trong thư mục source:

```text
xelatex main.tex
bibtex main
xelatex main.tex
xelatex main.tex
```

## Bảng, hình và nguồn số liệu

Source ZIP đã chứa các tài nguyên để compile độc lập. Trong repository,
`build_assets.py` tạo lại bảng/hình từ CSV tại
`artifacts/local/pc-exploratory-20261030/final-report/`, sử dụng môi trường
Python nghiên cứu đã khóa. `source_manifest.json` lưu SHA256 của input, source
và từng tài nguyên được tạo. Việc dựng báo cáo không train hoặc inference lại.

```powershell
./.venv/Scripts/python.exe docs/latex/build_assets.py
./docs/latex/compile.ps1
./.venv/Scripts/python.exe docs/latex/package_source.py
```

Số liệu giữ nguyên snapshot đã đánh giá; báo cáo trình bày ảnh hưởng của nhãn
Open, lựa chọn checkpoint và phạm vi kết luận trong phần phương pháp/thảo luận.
Thời gian **SFT 5 epoch/seed** được đo sau setup/encode, không phải thời gian
download, pre-training hoặc toàn bộ pipeline. Các hàng SFT dùng best-trained;
selected checkpoint có xét epoch 0 được ghi riêng.

`release_manifest.json` trong repository lưu hash PDF và ZIP bàn giao.
Không đóng gói font hệ thống, môi trường Python hoặc công cụ biên dịch.
