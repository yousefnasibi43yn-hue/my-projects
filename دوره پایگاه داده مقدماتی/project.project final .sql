-----مدریت محترم/مدیریت محترم انبار
--گزارش تحلیل ماندگاری موجودی انبار به شرح زیر میباشد 
--تحلیل‌گر: یوسف نصیبی
--هدف: شناسایی کالاهایی که در آستانه اتمام موجودی هستند و مانگداری پایینی براشون پیش بینی شده است 
--==========================================================================================================

--:کوئری اول 
SELECT
o.order_id,                 -- شناسه منحصر به فرد هر سفارش
o.order_date,               -- تاریخ ثبت سفارش
st.store_id,                -- شناسه فروشگاهی که سفارش در آن ثبت شده
c.customer_id AS customer_id, -- شناسه مشتری که سفارش را داده
p.brand_id,                 -- شناسه برند کالای موجود در سفارش
oi.quantity,                -- تعداد کالای سفارش داده شده در این آیتم
oi.list_price,              -- قیمت پایه کالا قبل از تخفیف
oi.discount,                -- میزان تخفیف اعمال شده (به صورت درصدی یا مبلغی)
s.quantity AS stock_quantity   -- تعداد موجودی همان کالا در همان فروشگاه در زمان اجرای کوئری
FROM sales.orders o
INNER JOIN sales.order_items oi ON o.order_id = oi.order_id
INNER JOIN sales.stores st ON o.store_id = st.store_id
INNER JOIN sales.customers c ON o.customer_id = c.customer_id
INNER JOIN production.products p ON oi.product_id = p.product_id
INNER JOIN production.stocks s ON p.product_id = s.product_id AND o.store_id = s.store_id;
--در این کوئری، اطلاعات فروشگاه، کالا، برند، دسته‌بندی و موجودی ، در یک خروجی واحد ترکیب شده‌اند
--هدف این کوئری فقط نمایش یکپارچه‌ی داده‌هاست و هیچ محاسبه‌ای روی ستون‌ها انجام نمی‌شود
--=======================================================================================================

-- :کوئری دوم
SELECT  s.store_id, p.product_id,
COUNT(DISTINCT oi.order_id) 'TotalOrders',          
SUM(oi.quantity) TotalQty,                   
SUM(oi.quantity*oi.list_price*(1 - oi.discount)) 'TotalSales',
CAST(SUM(oi.quantity)* 1.0 / COUNT(DISTINCT oi.order_id) AS DECIMAL(15,2)) 'Avgqty',
CAST(SUM(oi.quantity*oi.list_price*(1 - oi.discount)) / SUM(oi.quantity) AS DECIMAL(15,2)) 'Avgunp'
FROM sales.order_items oi
INNER JOIN sales.orders o ON o.order_id = oi.order_id
INNER JOIN sales.stores s ON s.store_id = o.store_id
INNER JOIN production.products p ON p.product_id = oi.product_id
GROUP BY s.store_id, p.product_id
ORDER BY s.store_id, p.product_id;
--کوئری بالا نشان میدهد 
--هر محصول چنتا سفارش داشته است 
--چه تعداد از این محصول فروخته شده است 
--مجموعه مبلغ فروش هر محصول در هر فروشگاه 
--میانگین تعداد در هر سفارش 
--میانگین قیمت فروش خالص هر واحد
--================================================================

--:کوئری سوم 
SELECT s.store_id,p.product_id,MIN(o.order_date) 'FirstSaleDate',MAX(o.order_date) 'LastSaleDate',
DATEDIFF(DAY, MIN(o.order_date), MAX(o.order_date)) 'SaleRangeDays'
FROM sales.order_items oi
INNER JOIN sales.orders o ON o.order_id = oi.order_id
INNER JOIN sales.stores s ON s.store_id = o.store_id
INNER JOIN production.products p ON p.product_id = oi.product_id
GROUP BY s.store_id,p.product_id
ORDER BY s.store_id, p.product_id;
-- این کوئری اولین و آخرین تاریخ فروش هر کالا در هر فروشگاه را نشان می‌دهد
-- و فاصله زمانی فروش آن کالا در همان فروشگاه را بر حسب روز محاسبه می‌کند
--=============================================================================================================

--:کوئری چهارم
;WITH CTE AS (SELECT o.store_id, oi.product_id, SUM(oi.quantity) AS 'TotalSold',
DATEDIFF(day, MIN(o.order_date), MAX(o.order_date)) AS 'DaysActive'
FROM sales.orders o
INNER JOIN sales.order_items oi ON o.order_id = oi.order_id
GROUP BY o.store_id, oi.product_id),
CTE2 AS (SELECT store_id, product_id, 
CAST(TotalSold * 1.0 / CASE WHEN DaysActive = 0 THEN 1 ELSE DaysActive END AS DECIMAL(10,2)) AS 'DailySalesRate'
FROM CTE) SELECT c2.store_id, c2.product_id, 
FLOOR(s.quantity / NULLIF(c2.DailySalesRate, 0)) AS 'durability' FROM CTE2 c2
LEFT JOIN production.stocks s ON c2.store_id = s.store_id AND c2.product_id = s.product_id
WHERE FLOOR(s.quantity / NULLIF(c2.DailySalesRate, 0)) > 1
ORDER BY c2.store_id, durability;
-- این کوئری پیش‌بینی می‌کند که موجودی فعلی هر کالا در هر فروشگاه، با توجه به نرخ فروش روزانه، تا چند روز آینده پاسخگوی تقاضا خواهد بود
-- کالا‌هایی را نشان می‌دهد که بیش از ۱ روز ذخیره دارند و در وضعیت بحرانی نیستند 
--===========================================================================================================================================

--:کوئری پنجم
;WITH CTE AS (SELECT o.store_id, oi.product_id, SUM(oi.quantity) 'TotalSold',
DATEDIFF(day, MIN(o.order_date), MAX(o.order_date)) 'DaysActive'
FROM sales.orders o
INNER JOIN sales.order_items oi ON o.order_id = oi.order_id
GROUP BY o.store_id, oi.product_id),
CTE2 AS (SELECT store_id, product_id, TotalSold, 
CASE WHEN DaysActive = 0 THEN 1 ELSE DaysActive END 'SafeDaysActive',
CAST(TotalSold * 1.0 / CASE WHEN DaysActive = 0 THEN 1 ELSE DaysActive END AS DECIMAL(10,2)) 'DailySalesRate'
FROM CTE)
SELECT c2.store_id, c2.product_id, 
FLOOR(s.quantity / NULLIF(c2.DailySalesRate, 0)) 'durability'
FROM CTE2 c2
LEFT JOIN production.stocks s ON c2.store_id = s.store_id AND c2.product_id = s.product_id
WHERE FLOOR(s.quantity / NULLIF(c2.DailySalesRate, 0)) <= 1
ORDER BY c2.store_id, durability;
--«این کوئری با محاسبه نرخ میانگین فروش روزانه هر کالا، مشخص می‌کند که موجودی فعلی انبار برای چند روز دیگر کافی است.
--در نهایت، کالاهایی که با وضعیت بحرانی (اتمام موجودی در یک روز یا کمتر) مواجه هستند، شناسایی و لیست می‌شوند
--==========================================================================================================================

--:کوئری ششم
;WITH CTE AS (SELECT o.store_id, oi.product_id,SUM(oi.quantity)'TotalSold',
DATEDIFF(day, MIN(o.order_date), MAX(o.order_date)) 'DaysActive'
FROM sales.orders o
INNER JOIN sales.order_items oi ON o.order_id = oi.order_id
GROUP BY o.store_id, oi.product_id),
CTE2 AS (SELECT store_id, product_id, TotalSold, 
CASE WHEN DaysActive = 0 THEN 1 ELSE DaysActive END 'SafeDaysActive',
CAST(TotalSold * 1.0 / CASE WHEN DaysActive = 0 THEN 1 ELSE DaysActive END AS DECIMAL(10,2))'DailySalesRate'
FROM CTE)
SELECT c2.store_id, c2.product_id, 
FLOOR(s.quantity / NULLIF(c2.DailySalesRate, 0)) 'durability'
FROM CTE2 c2
LEFT JOIN production.stocks s ON c2.store_id = s.store_id AND c2.product_id = s.product_id
ORDER BY c2.store_id, durability;
--این کوئری با محاسبه نرخ میانگین فروش روزانه، برای هر محصول در هر فروشگاه
--تخمین میزند که موجودی فعلی انبار برای چند روز اینده پاسخگو تقاضا خواهد بود
--این فهرست نشان دهنده مدت زمان ماندگاری انها است
--که به تفکیک فروشگاه مرتب شده است
--سه کالا در این مرحله نامشخص هستند 
--که به تفکیک :
--ثبت نشده اند  'production_stocks'  ای دی 314 و 315 در 
--وای دی 29 به علت سرعت فروش صفر
--محاسبه ماندگاری ان ها با تداخل رو به رو شده است 
--=====================================================================================================================  

--======================================================================================================================= 
--:نتیجه‌گیری و تحلیل نهایی

--تحلیل فروش و موجودی نشان می‌دهد که در حال حاضر ۳۶ محصول در وضعیت بحرانی قرار دارند:
--- فروشگاه یک: ۱۶ محصول
--- فروشگاه دو: ۱۳ محصول
--- فروشگاه سه: ۷ محصول
--در صورت عدم مدیریت مناسب، این موضوع منجر به از دست رفتن فروش و اختلال در تأمین کالا می‌شود.

--:پیشنهاد

--برای کالاهای با ماندگاری پایین، بازنگری در زمان و مقدار سفارش‌گذاری انجام شود 
--و برای هر فروشگاه، سطح موجودی ایمن بر اساس الگوی واقعی فروش تعریف گردد.
--پایش مستمر این موارد به تصمیم‌گیری دقیق‌تر مدیر انبار کمک خواهد کرد.
--========================================================================================================================