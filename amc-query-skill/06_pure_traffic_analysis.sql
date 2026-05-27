-- =========================================================================================
-- BÁO CÁO PHÂN TÍCH LƯỢNG TRUY CẬP THUẦN TÚY (TRAFFIC ANALYSIS)
-- Mục đích: Bảng "conversion_time" có thể bị trễ dữ liệu mua hàng. Bảng "traffic_time" 
-- giúp bạn xem luồng traffic (Click/Impression) TỨC THÌ chính xác nhất theo thời gian tương tác.
-- =========================================================================================

SELECT
    ad_product_type AS loai_quang_cao,
    
    -- Đếm số lượng nhà quảng cáo độc lập (Mặc định bắt buộc dùng COUNT DISTINCT)
    COUNT(DISTINCT advertiser_id_internal) AS so_luong_advertiser,
    
    SUM(impressions) AS traffic_impressions,     -- Lượt hiển thị ghi nhận theo thời gian thực
    SUM(clicks) AS traffic_clicks,               -- Lượt click ghi nhận theo thời gian thực
    
    -- Tỷ lệ nhấp chuột (CTR) dựa trên traffic time
    ROUND(SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0) * 100, 2) AS ctr_pct

-- LƯU Ý: Ở ĐÂY SỬ DỤNG BẢNG TRAFFIC_TIME, KHÔNG PHẢI CONVERSION_TIME
FROM amazon_attributed_events_by_traffic_time

GROUP BY 1
ORDER BY traffic_clicks DESC