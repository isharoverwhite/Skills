-- =========================================================================================
-- BÁO CÁO HIỆU SUẤT THEO KÍCH THƯỚC/VỊ TRÍ QUẢNG CÁO (AD SLOT SIZE)
-- Mục đích: Phân tích xem banner quảng cáo kích thước nào (hoặc vị trí nào) mang lại 
-- tỷ lệ click (CTR) và tỷ suất lợi nhuận tốt nhất.
-- =========================================================================================

SELECT
    ad_slot_size AS kich_thuoc_quang_cao,        -- Kích thước/Vị trí slot quảng cáo
    ad_product_type AS loai_quang_cao,           -- Sponsored Brands / Sponsored Products
    
    SUM(impressions) AS total_impressions,       -- Tổng hiển thị
    SUM(clicks) AS total_clicks,                 -- Tổng lượt click
    SUM(product_sales) AS total_revenue,         -- Tổng doanh thu mang lại
    
    -- Tỷ lệ Click / Hiển thị (CTR) để đo độ thu hút của kích thước đó
    ROUND(SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0) * 100, 2) AS ctr_do_thu_hut_pct,
    
    -- Doanh thu trên mỗi lượt click (RPC) để xem kích thước nào sinh lời tốt hơn
    ROUND(SUM(product_sales) / NULLIF(SUM(clicks), 0), 2) AS rpc_doanh_thu_tren_click

FROM amazon_attributed_events_by_conversion_time

-- Lọc bỏ các dòng không ghi nhận kích thước quảng cáo
WHERE ad_slot_size IS NOT NULL 
  AND ad_slot_size != ''

GROUP BY 1, 2
ORDER BY total_revenue DESC