-- =========================================================================================
-- BÁO CÁO PHÂN TÍCH TỶ LỆ THOÁT GIỎ HÀNG (CART ABANDONMENT) THEO SẢN PHẨM (ASIN)
-- Mục đích: Tìm ra những sản phẩm khách hàng rất thích (Thêm vào giỏ nhiều) nhưng lại không mua.
-- Từ đó có thể tối ưu lại giá bán, mã giảm giá (coupon), hoặc xem xét phí vận chuyển.
-- =========================================================================================

SELECT
    tracked_asin AS ma_san_pham,
    
    SUM(add_to_cart) AS tong_lan_them_vao_gio,   -- Tổng số lần khách ấn "Add to cart"
    SUM(purchases) AS tong_don_mua,              -- Tổng số lần thanh toán thành công
    
    -- Số lượng bị bỏ lại trong giỏ hàng = Tổng thêm giỏ - Tổng mua
    (SUM(add_to_cart) - SUM(purchases)) AS so_luong_bi_bo_gio_hang,
    
    -- Tỷ lệ thoát giỏ hàng = (Số lượng bỏ / Tổng thêm giỏ) * 100
    ROUND((SUM(add_to_cart) - SUM(purchases)) * 1.0 / NULLIF(SUM(add_to_cart), 0) * 100, 2) AS ty_le_thoat_gio_hang_pct

FROM amazon_attributed_events_by_conversion_time

-- Nhóm theo Mã sản phẩm
GROUP BY 1

-- Chỉ lấy những sản phẩm CÓ được thêm vào giỏ hàng (loại bỏ dữ liệu rác)
HAVING SUM(add_to_cart) > 0

-- Sắp xếp theo số lượng bị bỏ lại nhiều nhất lên đầu để ưu tiên xử lý
ORDER BY so_luong_bi_bo_gio_hang DESC

LIMIT 50