#!/usr/bin/env python
# coding: utf-8

# In[1]:


import time
import os
import numpy as np
import random

from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, execute
from qiskit.tools.visualization import plot_histogram

from quantuminspire.credentials import get_authentication
from quantuminspire.qiskit import QI

QI_URL = os.getenv('API_URL', 'https://api.quantum-inspire.com/')


# In[2]:


authentication = get_authentication()
QI.set_authentication(authentication, QI_URL)


# In[3]:


def BB84Circuit(nbits, AliceBasis, BobBasis, message, bitPosition):
   
    """
    Circuit Generator
    
    nbits: Self-explainatory
    AliceBasis: nqubits-length array with entries 0 (z basis) or 1 (x basis)
    BobBasis: nqubits-length array with entries 0 (z basis) or 1 (x basis)
    message: nqubits-length binary array
    bitPosition: index of the bit in message to be communicated
    """
    q = QuantumRegister(1)
    ans = ClassicalRegister(1)
    qc = QuantumCircuit(q, ans)
    if message[bitPosition] == 1:
        qc.x(q[0])
    qc.barrier()
    
    if (AliceBasis[bitPosition] + BobBasis[bitPosition])%2 == 1:
        qc.h(q[0])

    qc.measure(q[0],ans[0])
    
    return q, qc


# In[42]:


nbits = 10
messageInABottle = []
AliceBasis = []
BobBasis = []
for i in range(nbits):
    
    messageInABottle.append(random.randint(0,1))
    AliceBasis.append(random.randint(0,1))
    BobBasis.append(random.randint(0,1))

print("Message: ", messageInABottle)
print("AliceBasis ", AliceBasis)
print("BobBasis ", BobBasis)


# In[8]:


def BB84Message(nbits,AliceBasis,BobBasis, message):
    """
    Constructs the Message with Quantum Magic
    nbits: Self-explainatory
    AliceBasis: nqubits-length array with entries 0 (z basis) or 1 (x basis)
    BobBasis: nqubits-length array with entries 0 (z basis) or 1 (x basis)
    message: nqubits-length binary array
    
    returns 
    constrMess (constructed message)
    sameBasisIndices (bit positions in which Alice and Bob use the same basis)
    
    """
    constrMess = []
    sameBasisIndices = []
    for bitPos in range(nbits):
        print("Quantum Communicating bit number: ",bitPos,"/",nbits)
        q, qc = BB84Circuit(nbits,AliceBasis,BobBasis,message,bitPos)
        qi_backend = QI.get_backend('QX-34-L')
        job = execute(qc, qi_backend)
        result = job.result()
        counts = result.get_counts()
        
        
        if (AliceBasis[bitPos]+ BobBasis[bitPos])%2 == 1: #different basis: trash
            constrMess.append("x")
            
        else: #same basis
            sameBasisIndices.append(bitPos)
            if len(counts)==1: #only one result
                constrMess.append(list(counts.keys())[0]) #add that result to the message
                
            else: #get the result with more counts
                if counts['0'] >= counts['1']:
                    constrMess.append('0')
                else:
                    constrMess.append('1')      
    
    return constrMess, sameBasisIndices    
        


# In[44]:


outputMes, goodIndices = BB84Message(nbits,AliceBasis,BobBasis,messageInABottle)


# In[45]:


print(outputMes)


# In[46]:


print(goodIndices)


# In[5]:


def BB84KeyConstruction(message,output,goodIndices,prop,tolerance):
    """
    message: Alice starting message
    output: Bob's result through Quantum Magic
    goodIndices: bit Positions in which both basis are the same    
    prop: Proportion of common good bits to be compared
    tolerance: minimum success rate to generate a safe QK

    """
    auxList = []    
    nGoodBits = len(goodIndices)
    
    
    nComparingBits = int(nGoodBits*prop)
    comparingBitPositions = random.sample(goodIndices, nComparingBits)
    print("Bit Positions to compare: ",comparingBitPositions)
    
    allOkCounter = 0
    for i in range(nComparingBits):
        j = comparingBitPositions[i]
        if int(message[j])== int(output[j]):
            allOkCounter +=1
            
    for i in range(nGoodBits):
        if i not in comparingBitPositions:
            auxList.append(output[goodIndices[i]])
    
    print(allOkCounter)
    successRate = float(allOkCounter/nComparingBits)
    print("Success rate: ",successRate)
    if successRate < tolerance:
        print("Failure")
        return 0
    else:
        print("Success!!!")
        return auxList

    


# In[48]:


prop = 0.5
tolerance = 0.8

QKD = BB84KeyConstruction(messageInABottle,outputMes,goodIndices,prop,tolerance)
print(QKD)


# In[6]:


def wholeBB84Protocol(nbits,prop,tolerance):
    messageInABottle = []
    AliceBasis = []
    BobBasis = []
    for i in range(nbits):

        messageInABottle.append(random.randint(0,1))
        AliceBasis.append(random.randint(0,1))
        BobBasis.append(random.randint(0,1))

    print("Message: ", messageInABottle)
    print("AliceBasis ", AliceBasis)
    print("BobBasis ", BobBasis)
    
    outputMes, goodIndices = BB84Message(nbits,AliceBasis,BobBasis,messageInABottle)
    print("Output Message: ",outputMes)
    print("Same Basis Instances: ",goodIndices)
    
    QKD = BB84KeyConstruction(messageInABottle,outputMes,goodIndices,prop,tolerance)
    print("Quantum Key Generated", QKD)
    
    return QKD
    
    


# In[9]:


nbits = 12
prop = 0.3
tolerance = 0.8
Key = wholeBB84Protocol(nbits,prop,tolerance)


# In[ ]:




