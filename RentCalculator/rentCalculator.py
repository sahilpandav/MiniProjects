rent = int(input("Enter Your room rent: "))
food = int(input("Enter the total amount of food ordered: "))
electbill = int(input("Enter amount of Electricity bill of this Month: "))
persons = int(input("Enter the numbers of persons living in room: "))


output = (rent + food + electbill) / persons

print("Each person should have to Pay: " , output)