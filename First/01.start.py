import random
min = 1
max = 100
count = 0
r = random.randint(min, max)


while True:
    num = int(input("请输入一个数字"))



    if num < r:
        count += 1
        min = num
        print(f"猜小了,结果在{min}到{max}之间")
    elif num > r:
        count += 1
        max = num
        print(f"猜大了,结果在{min}到{max}之间")
    else :
        print ("猜中了")
        break


print(f"恭喜你,一共猜了{count}次")
