select
        currency,
        title,
        round(CAST((rate/quantity) as numeric), 3) as rate,
        date as upload_date

from {{ source("stage", "currency_kzt")}}