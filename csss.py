# import execjs
# ctx=execjs.compile(open('cs.js', 'r', encoding='gb2312', errors='ignore').read())
# string = ctx.call('my_function')
# print(string)
from faker import Faker
# 中文需要使用zh_CN
fake = Faker('zh_CN')
# print('随机女性名称:')
for i in range(10):
    print(fake.paragraph())