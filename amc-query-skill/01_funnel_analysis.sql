-- =========================================================================================
-- BÁO CÁO PHÂN TÍCH PHỄU CHUYỂN ĐỔI (FUNNEL ANALYSIS)
-- Mục đích: Đánh giá chi tiết tỷ lệ khách hàng "rơi rụng" qua từng bước mua hàng.
-- Từ lúc nhìn thấy quảng cáo -> Bấm vào -> Thêm vào giỏ hàng -> Thanh toán thành công.
-- =========================================================================================

SELECT
    -- Gom các dòng không có loại quảng cáo thành nhóm 'Tự nhiên / Không xác định'
    -- Điều này giúp giữ lại toàn bộ doanh thu organic thay vì loại bỏ chúng
    COALESCE(ad_product_type, 'Tự nhiên / Không xác định') AS traffic_source,
    
    -- Các chỉ số tổng quan cơ bản
    SUM(impressions) AS total_impressions,       -- Tổng lượt hiển thị
    SUM(clicks) AS total_clicks,                 -- Tổng lượt click
    SUM(add_to_cart) AS total_add_to_cart,       -- Tổng số lần thêm vào giỏ hàng
    SUM(purchases) AS total_purchases,           -- Tổng số đơn hàng (lượt mua)
    SUM(product_sales) AS total_revenue,         -- Tổng doanh thu mang lại
    
    -- ========================================================================
    -- PHẦN PHÂN TÍCH TỶ LỆ CHUYỂN ĐỔI QUA TỪNG BƯỚC PHỄU
    -- Lưu ý: Dùng hàm NULLIF để tránh lỗi chia cho 0 (Divide by Zero)
    -- ========================================================================
    
    -- 1. Tỷ lệ Click / Hiển thị (CTR): Xem độ hấp dẫn của hình ảnh/tiêu đề quảng cáo
    ROUND(SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0) * 100, 2) AS impression_to_click_pct,
    
    -- 2. Tỷ lệ Thêm giỏ hàng / Click: Xem nội dung trang chi tiết (Detail Page) có thuyết phục không
    ROUND(SUM(add_to_cart) * 1.0 / NULLIF(SUM(clicks), 0) * 100, 2) AS click_to_cart_pct,
    
    -- 3. Tỷ lệ Mua hàng / Thêm giỏ hàng: Đánh giá xem giá cả/phí ship có làm khách chùn bước lúc thanh toán không
    ROUND(SUM(purchases) * 1.0 / NULLIF(SUM(add_to_cart), 0) * 100, 2) AS cart_to_purchase_pct

FROM amazon_attributed_events_by_conversion_time

-- Nhóm theo cột đầu tiên (traffic_source)
GROUP BY 1

-- Sắp xếp giảm dần theo doanh thu để xem nguồn nào đem lại nhiều tiền nhất
ORDER BY total_revenue DESC
