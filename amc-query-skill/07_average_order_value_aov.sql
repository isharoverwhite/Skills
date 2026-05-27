-- =========================================================================================
-- BÁO CÁO PHÂN TÍCH GIÁ TRỊ TRUNG BÌNH ĐƠN HÀNG (AVERAGE ORDER VALUE - AOV)
-- Mục đích: Tìm ra những chiến dịch hoặc nhóm khách hàng chịu chi tiền nhiều nhất trên 1 đơn hàng.
-- Từ đó, bạn có thể đẩy mạnh ngân sách vào các chiến dịch mang lại "khách sộp".
-- =========================================================================================

SELECT
    COALESCE(campaign_id, 'Tự nhiên / Không xác định') AS campaign_id_or_organic,
    ad_product_type AS loai_quang_cao,
    
    SUM(purchases) AS total_purchases,           -- Tổng số đơn hàng
    SUM(product_sales) AS total_revenue,         -- Tổng doanh thu
    
    -- ========================================================================
    -- CHỈ SỐ AOV (AVERAGE ORDER VALUE)
    -- Công thức: Tổng doanh thu / Tổng số đơn hàng
    -- ========================================================================
    ROUND(SUM(product_sales) / NULLIF(SUM(purchases), 0), 2) AS aov_gia_tri_trung_binh_don_hang

FROM amazon_attributed_events_by_conversion_time

-- Chỉ xét những chiến dịch có sinh ra ít nhất 1 đơn hàng để tránh dữ liệu rác
WHERE purchases > 0

GROUP BY 1, 2

-- Lọc tiếp: Chỉ quan tâm đến các chiến dịch mang lại từ 5 đơn hàng trở lên (để đảm bảo tính thống kê)
HAVING SUM(purchases) >= 5

-- Sắp xếp theo những chiến dịch có giá trị đơn hàng cao nhất lên đầu
ORDER BY aov_gia_tri_trung_binh_don_hang DESC

LIMIT 50