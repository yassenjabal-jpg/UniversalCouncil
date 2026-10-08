from decimal import Decimal, ROUND_HALF_EVEN

class CurrencyError(ValueError):
    pass

# ISO-style minor digit defaults needed by the current Iraqi operating context.
# Extend only with verified currency metadata.
MINOR_DIGITS = {
    "IQD": 3,
    "USD": 2,
}

def minor_digits(currency):
    try:
        return MINOR_DIGITS[currency]
    except KeyError as exc:
        raise CurrencyError(f"unknown currency precision: {currency}") from exc

def convert_minor(amount_minor, source_currency, target_currency, rate_text):
    """Convert minor units using a major-unit FX rate.

    rate_text means target major units per 1 source major unit.
    Example: 1 IQD = 0.00076 USD.
    """
    amount_minor = int(amount_minor)
    if amount_minor < 0:
        raise CurrencyError("negative conversion amount is invalid")

    src_scale = Decimal(10) ** minor_digits(source_currency)
    dst_scale = Decimal(10) ** minor_digits(target_currency)
    source_major = Decimal(amount_minor) / src_scale
    target_major = source_major * Decimal(str(rate_text))
    target_minor = target_major * dst_scale
    return int(target_minor.quantize(Decimal("1"), rounding=ROUND_HALF_EVEN))
