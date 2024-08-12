from django import template

import math
register = template.Library()

@register.simple_tag

def call_sellprice(marked_price, Discount_price):
    if Discount_price is None or Discount_price is 0:
        return marked_price
    sellprice = marked_price
    sellprice = marked_price -(marked_price * Discount_price/100)
    return math.floor(sellprice)