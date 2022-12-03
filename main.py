from smpc import VirtualMachine, PrivateScalar, SharedScalar
from encryption import dealer
from keys import *


#El Gamal Encryption and key generation.
MOD = 10001112223334445556667778889991
generation()
with open('ip.txt', 'r') as f:
    data = f.readlines()

num_iter = len(data)
messages=[]
messages=dealer(data)

#Initialization
P1=VirtualMachine('P1')
P2=VirtualMachine('P2')
P3=VirtualMachine('P3')

#Generation of data
a = PrivateScalar(int(messages[0]), P1)
b = PrivateScalar(int(messages[1]), P2)
c = PrivateScalar(int(messages[2]), P3) 

#Secret Sharing Generation of Parties
shared_P1=a.share([P1,P2,P3])
shared_P2=b.share([P1,P2,P3])
shared_P3=c.share([P1,P2,P3])

#Circuit construction: m1*m2+m3
shared_product=shared_P1*shared_P2
shared_result=shared_product+shared_P3

#Reconstruction
result=shared_result.reconstruct(P1)

with open('message.txt', 'w') as f:
    f.write(str(result))