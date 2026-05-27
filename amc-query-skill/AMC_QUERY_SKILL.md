# AMC Query Skill — Amazon Marketing Cloud
> Instance: Sponsored Ads (Vietnam)
> Confirmed columns: `purchases`, `clicks`, `impressions`, `product_sales`, `ad_product_type`, `advertiser_id_internal`
> SQL dialect: Apache Calcite (NO `DATE()`, NO `SELECT *`, NO `EXCEPT`)

---

## AMC SQL Rules (quan trọng)

| ❌ KHÔNG dùng | ✅ THAY BẰNG |
|---|---|
| `DATE(col)` | `DATE 'YYYY-MM-DD'` literal |
| `SELECT *` | Liệt kê cột cụ thể |
| `SELECT * EXCEPT (col)` | Bỏ cột đó ra khỏi SELECT |
| `impression_time` / `event_date` | Không có — dùng tab date filter |
| `purchases_14d` / `sales_14d` | `purchases` / `product_sales` |
| `revenue` / `sales` | `product_sales` |
| Cột `advertiser_id_internal` trong SELECT | `COUNT(DISTINCT advertiser_id_internal)` |

---

## Date Range Guide — Quan trọng cho AI Agents

### Cách AMC xử lý thời gian
AMC **KHÔNG dùng WHERE clause để filter ngày** trong SQL. Thay vào đó, date range được set ở **tab Settings** trên Query Editor UI. SQL chỉ cần viết logic aggregation thuần túy.

| ❌ SAI — sẽ gây parse error | ✅ ĐÚNG |
|---|---|
| `WHERE event_date = DATE '2026-05-25'` | Bỏ WHERE date, set date ở Settings tab |
| `WHERE impression_time >= TIMESTAMP '...'` | Bỏ WHERE date, set date ở Settings tab |
| `WHERE conversion_time BETWEEN ... AND ...` | Bỏ WHERE date, set date ở Settings tab |

### Cách chuyển đổi date range

**Bước 1:** Viết SQL không có WHERE date filter
**Bước 2:** Bấm tab **Settings** trên Query Editor
**Bước 3:** Chọn date range phù hợp

| Mục tiêu | Chọn trong Settings |
|---|---|
| Hôm qua | `Yesterday` (mặc định) |
| 7 ngày gần nhất | `Last 7 days` |
| 30 ngày gần nhất | `Last 30 days` |
| Tháng này | `This month` |
| Tuỳ chỉnh | `Custom range` → nhập ngày bắt đầu & kết thúc |

### Ví dụ chuyển đổi

**Phân tích ngày 25/05/2026:**
→ Vào Settings → Custom range → 2026-05-25 đến 2026-05-25

**Phân tích tuần 19-25/05/2026:**
→ Vào Settings → Custom range → 2026-05-19 đến 2026-05-25

**Phân tích tháng 5/2026:**
→ Vào Settings → Custom range → 2026-05-01 đến 2026-05-31

### Lưu ý cho AI Agents
- SQL trong AMC là **stateless về thời gian** — không biết đang query ngày nào
- Date range filter là **UI-level config**, không phải SQL-level
- Nếu user yêu cầu "doanh số tuần này" → nhắc user set date range trong Settings, không thêm WHERE vào SQL
- Lỗi `A syntax error... Are you missing <WITH> or <SELECT>?` thường do cố gắng dùng WHERE date filter sai cú pháp

---

## Skill 1 — Tổng quan doanh số theo ad type

```sql
SELECT
    ad_product_type,
    COUNT(DISTINCT advertiser_id_internal)               AS advertiser_count,
    SUM(purchases)                                       AS total_purchases,
    SUM(clicks)                                          AS total_clicks,
    SUM(impressions)                                     AS total_impressions,
    SUM(product_sales)                                   AS total_revenue,
    ROUND(
      SUM(purchases) * 1.0
      / NULLIF(SUM(clicks), 0) * 100, 2)                AS cvr_pct,
    ROUND(
      SUM(product_sales)
      / NULLIF(SUM(purchases), 0), 2)                   AS avg_order_value,
    ROUND(
      SUM(clicks) * 1.0
      / NULLIF(SUM(impressions), 0) * 100, 2)           AS ctr_pct
FROM amazon_attributed_events_by_conversion_time
GROUP BY 1
ORDER BY total_revenue DESC
```

**Kết quả đã verify (Yesterday filter):**
- sponsored_brands: purchases=0, clicks=3, impressions=11, revenue=0.0
- sponsored_products: purchases=10, clicks=11, impressions=?, revenue=230.9

---

## Skill 2 — Doanh số theo campaign

```sql
SELECT
    ad_product_type,
    campaign_id,
    COUNT(DISTINCT advertiser_id_internal)               AS advertiser_count,
    SUM(purchases)                                       AS total_purchases,
    SUM(clicks)                                          AS total_clicks,
    SUM(impressions)                                     AS total_impressions,
    SUM(product_sales)                                   AS total_revenue,
    ROUND(
      SUM(purchases) * 1.0
      / NULLIF(SUM(clicks), 0) * 100, 2)                AS cvr_pct,
    ROUND(
      SUM(product_sales)
      / NULLIF(SUM(purchases), 0), 2)                   AS avg_order_value
FROM amazon_attributed_events_by_conversion_time
GROUP BY 1, 2
ORDER BY total_revenue DESC
```

---

## Skill 3 — Top ASIN bán chạy

```sql
SELECT
    tracked_asin,
    ad_product_type,
    COUNT(DISTINCT advertiser_id_internal)               AS advertiser_count,
    SUM(purchases)                                       AS total_purchases,
    SUM(product_sales)                                   AS total_revenue,
    SUM(clicks)                                          AS total_clicks,
    ROUND(
      SUM(product_sales)
      / NULLIF(SUM(purchases), 0), 2)                   AS avg_order_value
FROM amazon_attributed_events_by_conversion_time
GROUP BY 1, 2
ORDER BY total_revenue DESC
LIMIT 20
```

---

## Skill 4 — CTR & CVR performance theo campaign

```sql
SELECT
    campaign_id,
    ad_product_type,
    COUNT(DISTINCT advertiser_id_internal)               AS advertiser_count,
    SUM(impressions)                                     AS impressions,
    SUM(clicks)                                          AS clicks,
    SUM(purchases)                                       AS purchases,
    SUM(product_sales)                                   AS revenue,
    ROUND(
      SUM(clicks) * 1.0
      / NULLIF(SUM(impressions), 0) * 100, 3)           AS ctr_pct,
    ROUND(
      SUM(purchases) * 1.0
      / NULLIF(SUM(clicks), 0) * 100, 2)                AS cvr_pct,
    ROUND(
      SUM(product_sales)
      / NULLIF(SUM(clicks), 0), 2)                      AS revenue_per_click
FROM amazon_attributed_events_by_conversion_time
GROUP BY 1, 2
ORDER BY revenue DESC
```

---

## Skill 5 — Add to cart analysis

```sql
SELECT
    ad_product_type,
    COUNT(DISTINCT advertiser_id_internal)               AS advertiser_count,
    SUM(add_to_cart)                                     AS total_add_to_cart,
    SUM(add_to_cart_clicks)                              AS add_to_cart_clicks,
    SUM(purchases)                                       AS total_purchases,
    ROUND(
      SUM(purchases) * 1.0
      / NULLIF(SUM(add_to_cart), 0) * 100, 2)           AS cart_to_purchase_pct
FROM amazon_attributed_events_by_conversion_time
GROUP BY 1
ORDER BY total_add_to_cart DESC
```

---

## Skill 6 — So sánh Sponsored Brands vs Sponsored Products

```sql
SELECT
    ad_product_type,
    COUNT(DISTINCT advertiser_id_internal)               AS advertiser_count,
    SUM(impressions)                                     AS impressions,
    SUM(clicks)                                          AS clicks,
    SUM(purchases)                                       AS purchases,
    SUM(product_sales)                                   AS revenue,
    ROUND(SUM(clicks) * 1.0
      / NULLIF(SUM(impressions), 0) * 100, 3)           AS ctr_pct,
    ROUND(SUM(purchases) * 1.0
      / NULLIF(SUM(clicks), 0) * 100, 2)                AS cvr_pct,
    ROUND(SUM(product_sales)
      / NULLIF(SUM(purchases), 0), 2)                   AS aov
FROM amazon_attributed_events_by_conversion_time
GROUP BY 1
```

---

## Bảng tham chiếu nhanh

### Bảng & mục đích sử dụng
| Bảng | Dùng cho |
|---|---|
| `amazon_attributed_events_by_conversion_time` | Conversion, purchases, revenue |
| `amazon_attributed_events_by_traffic_time` | Traffic analysis, clicks theo thời gian |
| `amazon_live_traffic` | Real-time traffic |
| `conversions` | Conversion funnel |
| `conversions_with_relevance` | Conversion + relevance score |
| `dsp_clicks` | DSP click data |
| `dsp_impressions` | DSP impression data |
| `dsp_impressions_by_matched_segments` | DSP audience segments |
| `dsp_impressions_by_user_segments` | DSP user segments |
| `dsp_video_events_feed` | DSP video events |
| `dsp_views` | DSP view data |
| `sponsored_ads_traffic` | Sponsored Ads traffic |

### Confirmed column names — amazon_attributed_events_by_conversion_time
| Column | Mô tả |
|---|---|
| `ad_product_type` | ✅ `sponsored_brands` hoặc `sponsored_products` |
| `ad_slot_size` | Kích thước slot quảng cáo |
| `add_to_cart` | Số lần thêm vào giỏ hàng |
| `add_to_cart_clicks` | Clicks dẫn đến add to cart |
| `campaign_id` | ✅ ID campaign |
| `tracked_asin` | ✅ ASIN sản phẩm được track |
| `purchases` | ✅ Số lần mua hàng |
| `clicks` | ✅ Số lần click |
| `impressions` | ✅ Số lần hiển thị |
| `product_sales` | ✅ Doanh thu (VD: 230.9) |
| `advertiser_id_internal` | ⚠️ Non-viewable — chỉ dùng COUNT(DISTINCT) |
| `advertiser_timezone` | Timezone của advertiser |

