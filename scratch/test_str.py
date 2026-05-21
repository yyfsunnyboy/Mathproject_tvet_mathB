# -*- coding: utf-8 -*-
s1 = '"\u8a66\u6c42 2-1\uff1d1\u3002"'
s2 = '--- Page 1 ---\n\u4f8b\u984cI\uff1a\\"\u8a66\u6c42 2-1\uff1d1\u3002\\"\n\n\n\n\n\n(1) \u7b2c\u4e00\u5c0f\u984c\u3002\n\n\n\n\n\n||\n'
print("s1:", repr(s1))
print("s2:", repr(s2))
print("s1 in s2:", s1 in s2)
print("s1 has backslashes:", '\\' in s1)
print("s2 has backslashes:", '\\' in s2)
