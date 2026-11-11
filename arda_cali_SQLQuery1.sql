CREATE DATABASE CUSTOMERS

CREATE TABLE FLO (
	master_id							VARCHAR(50),
	order_channel						VARCHAR(50),
	last_order_channel					VARCHAR(50),
	first_order_date					DATE,
	last_order_date						DATE,
	last_order_date_online				DATE,
	last_order_date_offline				DATE,
	order_num_total_ever_online			INT,
	order_num_total_ever_offline		INT,
	customer_value_total_ever_offline	FLOAT,
	customer_value_total_ever_online	FLOAT,
	interested_in_categories_12			VARCHAR(50),
	store_type							VARCHAR(10)
);

SELECT COUNT(DISTINCT master_id) AS TEKIL_KISI_SAYISI, COUNT(master_id) as MUSTERI_ADET  FROM [CUSTOMERS].[dbo].[flo];

SELECT 
	SUM(order_num_total_ever_offline + order_num_total_ever_online) AS TOPLAM_SIPARIS_SAYISI,
	ROUND(SUM(customer_value_total_ever_offline + customer_value_total_ever_online), 2) AS TOPLAM_CIRO
FROM [CUSTOMERS].[dbo].[flo];

SELECT  
SUM(order_num_total_ever_online+order_num_total_ever_offline) ToplamSiparisMiktari
	ROUND(
	(
	SUM(customer_value_total_ever_offline + customer_value_total_ever_online) / 
	SUM(order_num_total_ever_online+order_num_total_ever_offline) 
	), 1) AS SIPARIS_ORT_CIRO 
 FROM [CUSTOMERS].[dbo].[flo]

 SELECT  
	last_order_channel AS SON_ALISVERIS_KANALI,
	SUM(customer_value_total_ever_offline + customer_value_total_ever_online) TOPLAMCIRO,
	SUM(order_num_total_ever_online+order_num_total_ever_offline) TOPLAM_SIPARIS_SAYISI
FROM [CUSTOMERS].[dbo].[flo]
GROUP BY  last_order_channel
order by TOPLAMCIRO DESC
;

SELECT 
	store_type AS MAGAZATURU, 
    ROUND(SUM(customer_value_total_ever_offline + customer_value_total_ever_online), 2) TOPLAM_CIRO 
FROM [CUSTOMERS].[dbo].[flo] 
GROUP BY store_type;

select DISTINCT store_type FROM [CUSTOMERS].[dbo].[flo] ;

SELECT Value,SUM(TOPLAM_CIRO/COUNT_) FROM
(
	SELECT 
		store_type AS MAGAZATURU,
		(SELECT 
			COUNT(VALUE) 
		FROM  string_split(store_type,',') ) AS COUNT_,
		ROUND(SUM(customer_value_total_ever_offline + customer_value_total_ever_online), 2) TOPLAM_CIRO 
	FROM [CUSTOMERS].[dbo].[flo]
	GROUP BY store_type) T
	CROSS APPLY (SELECT  VALUE  FROM  string_split(T.MAGAZATURU,',')
) D
GROUP BY Value;

SET STATISTICS TIME ON;

SELECT 
	YEAR(first_order_date) YIL,  
	SUM(order_num_total_ever_offline + order_num_total_ever_online) SIPARIS_SAYISI
FROM  [CUSTOMERS].[dbo].[flo]
GROUP BY YEAR(first_order_date)
ORDER BY YIL DESC;

SET STATISTICS TIME OFF;
-- select DISTINCT first_order_date FROM [CUSTOMERS].[dbo].[flo] ;

SELECT last_order_channel, 
       ROUND(SUM(customer_value_total_ever_offline + customer_value_total_ever_online),2) TOPLAM_CIRO,
	   SUM(order_num_total_ever_offline + order_num_total_ever_online) TOPLAM_SIPARIS_SAYISI,
       ROUND(SUM(customer_value_total_ever_offline + customer_value_total_ever_online) / SUM(order_num_total_ever_offline + order_num_total_ever_online),2) AS VERIMLILIK
FROM [CUSTOMERS].[dbo].[flo]
GROUP BY last_order_channel
order by last_order_channel DESC;


SELECT interested_in_categories_12, 
       COUNT(*) FREKANS_BILGISI 
FROM [CUSTOMERS].[dbo].[flo]
GROUP BY interested_in_categories_12
ORDER BY 2 DESC;


SELECT TOP 1  
	store_type, 
    COUNT(*) FREKANS_BILGISI 
FROM [CUSTOMERS].[dbo].[flo] 
GROUP BY store_type 
ORDER BY 2 DESC;

SELECT DISTINCT last_order_channel,
(
	SELECT top 1 interested_in_categories_12
	FROM [CUSTOMERS].[dbo].[flo]  WHERE last_order_channel=f.last_order_channel
	group by interested_in_categories_12
	order by 
	SUM(order_num_total_ever_online+order_num_total_ever_offline) desc 
) "EN COK ILGI GOREN KATEGORI" , 
(
	SELECT top 1 SUM(order_num_total_ever_online+order_num_total_ever_offline)
	FROM [CUSTOMERS].[dbo].[flo]  WHERE last_order_channel=f.last_order_channel
	group by interested_in_categories_12
	order by 
	SUM(order_num_total_ever_online+order_num_total_ever_offline) desc 
) as "TOPLAM SIPARIS SAYISI"
FROM [CUSTOMERS].[dbo].[flo] F

 SELECT TOP 1 master_id   		    
	FROM [CUSTOMERS].[dbo].[flo] 
	GROUP BY master_id 
ORDER BY  SUM(order_num_total_ever_online+order_num_total_ever_offline) DESC 

 SELECT TOP 1 master_id   		    
	FROM [CUSTOMERS].[dbo].[flo] 
	GROUP BY master_id 
ORDER BY  SUM(customer_value_total_ever_offline + customer_value_total_ever_online) DESC 

SELECT 
	D.master_id,
	ROUND((D.TOPLAM_CIRO / D.TOPLAM_SIPARIS_SAYISI),2) SIPARIS_BASINA_ORTALAMA,
	TOPLAM_SIPARIS_SAYISI,
	DATEDIFF(DAY, first_order_date, last_order_date) as DAY_DIF,
	ROUND((DATEDIFF(DAY, first_order_date, last_order_date)/D.TOPLAM_SIPARIS_SAYISI ),2) ALISVERIS_GUN_ORT
FROM
(
SELECT TOP 1 master_id, first_order_date, last_order_date,
		   SUM(customer_value_total_ever_offline + customer_value_total_ever_online) as TOPLAM_CIRO,
		   SUM(order_num_total_ever_offline + order_num_total_ever_online) as TOPLAM_SIPARIS_SAYISI
	FROM [CUSTOMERS].[dbo].[flo] 
	GROUP BY master_id,first_order_date, last_order_date
ORDER BY TOPLAM_CIRO DESC
) D

SELECT  
D.master_id,
       D.TOPLAM_CIRO,
	   D.TOPLAM_SIPARIS_SAYISI,
       ROUND((D.TOPLAM_CIRO / D.TOPLAM_SIPARIS_SAYISI),2) SIPARIS_BASINA_ORTALAMA,
	   DATEDIFF(DAY, first_order_date, last_order_date) ILK_SN_ALVRS_GUN_FRK,
	  ROUND((DATEDIFF(DAY, first_order_date, last_order_date)/D.TOPLAM_SIPARIS_SAYISI ),1) ALISVERIS_GUN_ORT	 
  FROM
(
SELECT TOP 100 master_id, first_order_date, last_order_date,
		   SUM(customer_value_total_ever_offline + customer_value_total_ever_online) TOPLAM_CIRO,
		   SUM(order_num_total_ever_offline + order_num_total_ever_online) TOPLAM_SIPARIS_SAYISI
	FROM [CUSTOMERS].[dbo].[flo] 
	GROUP BY master_id,first_order_date, last_order_date
ORDER BY TOPLAM_CIRO DESC
) D

SELECT DISTINCT last_order_channel,
(
	SELECT top 1 master_id
	FROM [CUSTOMERS].[dbo].[flo]  WHERE last_order_channel=f.last_order_channel
	group by master_id
	order by 
	SUM(customer_value_total_ever_offline+customer_value_total_ever_online) desc 
) EN_COK_ALISVERIS_YAPAN_MUSTERI,
(
	SELECT top 1 SUM(customer_value_total_ever_offline+customer_value_total_ever_online)
	FROM [CUSTOMERS].[dbo].[flo]  WHERE last_order_channel=f.last_order_channel
	group by master_id
	order by 
	SUM(customer_value_total_ever_offline+customer_value_total_ever_online) desc 
) CIRO
FROM [CUSTOMERS].[dbo].[flo] F

SELECT master_id,last_order_date FROM [CUSTOMERS].[dbo].[flo]
WHERE last_order_date=(SELECT MAX(last_order_date) FROM [CUSTOMERS].[dbo].[flo])