select
        title,
        1/rate as rate,
        date as upload_date

from {{ source("stage", "currency_usd") }}