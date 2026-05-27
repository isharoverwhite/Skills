-- =========================================================================================
-- BÁO CÁO PHÂN TÍCH ASIN: DOANH THU QUẢNG CÁO (PAID) VS TỰ NHIÊN (ORGANIC)
-- Mục đích: Đánh giá sức khỏe của từng mã sản phẩm (ASIN).
-- Trả lời câu hỏi: Sản phẩm này đang sống dựa vào tiền chạy Ads, hay tự nó đã thu hút khách?
-- =========================================================================================

SELECT
    tracked_asin AS ma_san_pham,                 -- Mã ASIN của sản phẩm
    
    -- Kiểm tra xem giao dịch này có thuộc chiến dịch quảng cáo nào không
    -- Dùng CASE WHEN để phân loại dòng dữ liệu
    CASE
        WHEN campaign_id IS NULL OR campaign_id = '' THEN 'Tự nhiên (Organic) / Không rõ nguồn'
        ELSE 'Đến từ Quảng cáo (Paid Ads)'
    END AS phan_loai_nguon_goc,
    
    -- Tổng hợp các chỉ số cơ bản
    SUM(impressions) AS total_impressions,       -- Số lượt hiển thị
    SUM(clicks) AS total_clicks,                 -- Số lượt click
    SUM(purchases) AS total_purchases,           -- Số đơn hàng
    SUM(product_sales) AS total_revenue,         -- Doanh thu
    
    -- ========================================================================
    -- CHỈ SỐ TỶ LỆ CHUYỂN ĐỔI (CONVERSION RATE)
    -- Tính tỷ lệ phần trăm: Cứ 100 người click thì có bao nhiêu người mua hàng
    -- ========================================================================
    ROUND(SUM(purchases) * 1.0 / NULLIF(SUM(clicks), 0) * 100, 2) AS ty_le_chuyen_doi_pct

FROM amazon_attributed_events_by_conversion_time

-- Nhóm dữ liệu theo Mã sản phẩm (cột 1) và Nguồn gốc (cột 2)
GROUP BY 1, 2

-- Xếp hạng theo doanh thu từ cao xuống thấp để tìm ra các sản phẩm trụ cột
ORDER BY total_revenue DESC

-- Chỉ lấy top 50 kết quả đầu tiên để báo cáo không bị quá dài
LIMIT 50
