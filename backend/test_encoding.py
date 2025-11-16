#!/usr/bin/env python3
"""
Test URL encoding differences
"""

from urllib.parse import quote, quote_plus

# The X-Goog-Credential value that's giving us trouble
value = "signed-url@storied-catwalk-476608-d1.iam.gserviceaccount.com/20251116/auto/storage/goog4_request"

print("Original value:")
print(f"  {value}")
print()

print("Encoded with quote(safe=''):")
encoded_safe_empty = quote(value, safe='')
print(f"  {encoded_safe_empty}")
print()

print("Encoded with quote() default:")
encoded_default = quote(value)
print(f"  {encoded_default}")
print()

print("Encoded with quote_plus():")
encoded_plus = quote_plus(value)
print(f"  {encoded_plus}")
print()

print("Analysis:")
print(f"  quote(safe='') encodes: / @ /")
print(f"  quote() default keeps: / @ /")
print(f"  quote_plus() also spaces to +")
print()

print("GCS expects (from error response):")
print(f"  signed-url%40storied-catwalk-476608-d1.iam.gserviceaccount.com%2F20251116%2Fauto%2Fstorage%2Fgoog4_request")
print()

print("Match with quote(safe=''):", encoded_safe_empty == "signed-url%40storied-catwalk-476608-d1.iam.gserviceaccount.com%2F20251116%2Fauto%2Fstorage%2Fgoog4_request")
