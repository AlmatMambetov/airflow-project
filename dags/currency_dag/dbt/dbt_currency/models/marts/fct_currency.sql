with usd as (
    select
        title,
        rate,
        upload_date
    from {{ ref("stg_usd") }}

),

pound as (
    select
        title,
        rate,
        upload_date
    from {{ ref("stg_pound") }}

),

rub as (
    select
        title,
        rate,
        upload_date
    from {{ ref("stg_rub") }}

),

kzt as (
    select
        currency,
        title,
        rate,
        upload_date
    from {{ ref("stg_kzt") }}

),

final as (
    SELECT kzt.currency,
           kzt.title,
           kzt.upload_date,
           kzt.rate as kzt_rate,
           usd.rate as usd_rate,
           pound.rate as pound_rate,
           rub.rate as rub_rate

        FROM kzt
        LEFT JOIN usd ON kzt.title = usd.title and kzt.upload_date = usd.upload_date
        LEFT JOIN pound ON kzt.title = pound.title and kzt.upload_date = pound.upload_date
        LEFT JOIN rub ON kzt.title = rub.title and kzt.upload_date = rub.upload_date

)


insert into fct_currency (currency, title, upload_date, kzt_rate, usd_rate, pound_rate, rub_rate)
select
    currency,
    title,
    upload_date,
    kzt_rate,
    usd_rate,
    pound_rate,
    rub_rate
from final