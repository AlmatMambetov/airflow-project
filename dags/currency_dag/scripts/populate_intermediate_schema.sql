INSERT INTO intermediate.currency
select f1.currency,
       f1.title,
       f1.rate as rate_kzt,
       f2.value as rate_rub,
       round(1/f3.rate::numeric, 3) as rate_usd,
       round(1/f4.rate::numeric, 3) as rate_pound,
       f1.date
from stage.currency_parsing_kzt f1
    left join stage.currency_parsing_rub f2
        on f1.date = f2.date and f1.title = f2.charcode
    left join stage.currency_parsing_usd f3
        on f1.date = f3.date and f1.title = f3.title
    left join stage.currency_parsing_pound f4
        on f1.date = f4.date and f1.title = f4.title;