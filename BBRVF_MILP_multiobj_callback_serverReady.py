#!/usr/bin/env python
# coding: utf-8

# In[1]:


'''
Created on Dec 12, 2023

@author: Samira Fallah (saf418@lehigh.edu)
'''


# In[2]:


import time
import argparse
from gurobipy import *
import math

# Absolute path to the libSym, extention change based on the OS:
# - Windows: .dll
# - Linux: .so
# - OSX: .dylib


# In[3]:


# This is the path pointing to the dynamic library
lib_path = r'/mnt/c/rvf_symphony/build-SYMPHONY-rvf/lib/libSym.so'
# server
# lib_path = r'/home/saf418/ValueFunctionCode/RVFCodes/SYMPHONYBBRVF/build-SYMPHONY-rvf/lib/libSym.so'

# Import the python package
from symphony import *

# Load the library by calling this static method
Symphony.dlopen(lib_path)


# In[4]:


# from MILP_obj_2_var_30_nzr_4_intR_95_u_1_ins_4 import *
# instancePy = 'MILP_obj_2_var_30_nzr_4_intR_95_u_1_ins_4.py'

# instance = 'MILP_obj_2_var_30_nzr_4_intR_95_u_1_ins_4.mps'
# model_path = r'/mnt/c/Users/falla/OneDrive - Lehigh University/Desktop/PhD/bbrvfcode/BBRVF/makeMPSFiles/MILP_MPS/{}'.format(instance)


# In[5]:


# from obj_4_var_10_nzr_6_intR_6_U_2_ins_3 import *
# instancePy = 'obj_4_var_10_nzr_6_intR_6_U_2_ins_3.py'

# instance = 'obj_4_var_10_nzr_6_intR_6_U_2_ins_3.mps'
# model_path = r'/mnt/c/Users/falla/OneDrive - Lehigh University/Desktop/PhD/bbrvfcode/BBRVF/makeMPSFiles/MILP_MPS/{}'.format(instance)


# In[6]:


# NDP
# from obj_3_var_10_nzr_4_intR_6_U_1_ins_3 import *
# instancePy = 'obj_3_var_10_nzr_4_intR_6_U_1_ins_3.py'

# instance = 'obj_3_var_10_nzr_4_intR_6_U_1_ins_3.mps'
# model_path = r'/mnt/c/Users/falla/OneDrive - Lehigh University/Desktop/PhD/bbrvfcode/BBRVF/makeMPSFiles/MILP_MPS/{}'.format(instance)


# In[7]:


# NDP 10
# from obj_3_var_15_nzr_5_intR_6_U_1_ins_3 import *
# instancePy = 'obj_3_var_15_nzr_5_intR_6_U_1_ins_3.py'

# instance = 'obj_3_var_15_nzr_5_intR_6_U_1_ins_3.mps'
# model_path = r'/mnt/c/Users/falla/OneDrive - Lehigh University/Desktop/PhD/bbrvfcode/BBRVF/makeMPSFiles/MILP_MPS/{}'.format(instance)


# In[8]:


# NDP 22
# from obj_3_var_15_nzr_5_intR_6_U_1_ins_5 import *
# instancePy = 'obj_3_var_15_nzr_5_intR_6_U_1_ins_5.py'

# instance = 'obj_3_var_15_nzr_5_intR_6_U_1_ins_5.mps'
# model_path = r'/mnt/c/Users/falla/OneDrive - Lehigh University/Desktop/PhD/bbrvfcode/BBRVF/makeMPSFiles/MILP_MPS/{}'.format(instance)


# In[9]:


# NDP 29
# from obj_3_var_25_nzr_5_intR_6_U_1_ins_4 import *
# instancePy = 'obj_3_var_25_nzr_5_intR_6_U_1_ins_4.py'

# instance = 'obj_3_var_25_nzr_5_intR_6_U_1_ins_4.mps'
# model_path = r'/mnt/c/Users/falla/OneDrive - Lehigh University/Desktop/PhD/bbrvfcode/BBRVF/makeMPSFiles/MILP_MPS/{}'.format(instance)


# In[10]:


# NDP 13
# from obj_4_var_10_nzr_5_intR_6_U_1_ins_0 import *
# instancePy = 'obj_4_var_10_nzr_5_intR_6_U_1_ins_0.py'

# instance = 'obj_4_var_10_nzr_5_intR_6_U_1_ins_0.mps'
# model_path = r'/mnt/c/Users/falla/OneDrive - Lehigh University/Desktop/PhD/bbrvfcode/BBRVF/makeMPSFiles/MILP_MPS/{}'.format(instance)


# In[11]:


# NDP 18
# from obj_4_var_15_nzr_5_intR_6_U_1_ins_0 import *
# instancePy = 'obj_4_var_15_nzr_5_intR_6_U_1_ins_0.py'

# instance = 'obj_4_var_15_nzr_5_intR_6_U_1_ins_0.mps'
# model_path = r'/mnt/c/Users/falla/OneDrive - Lehigh University/Desktop/PhD/bbrvfcode/BBRVF/makeMPSFiles/MILP_MPS/{}'.format(instance)


# In[12]:


# adding Folder to the system path
sys.path.insert(0, r'/home/saf418/ValueFunctionCode/RVFCodes/SYMPHONYBBRVF/Test_py_MILP_multiobj')

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--instance", help = "specify the instance")
parser.add_argument("-j", "--samplesize", help = "specify the sample size")
flags = parser.parse_args()
instance = flags.instance 
instanceName = instance.split('.mps')[0]
initial_sample_size = int(flags.samplesize) 
n_in_sample_size = initial_sample_size
for key, val in vars(__import__(instanceName)).items():
    if key.startswith('__') and key.endswith('__'):
        continue
    vars()[key] = val
    
model_path = r'/home/saf418/ValueFunctionCode/RVFCodes/SYMPHONYBBRVF/Test_MPS_MILP_multiobj/{}'.format(instance)


# In[13]:


# local
# initial_sample_size = 5
# n_in_sample_size = initial_sample_size


# In[14]:


timeLimit = 14400

debug_print = False
mipForU = True


# In[15]:


def changeValue(value):
    if str(value) == 'None':
        return 0.0
    return value


# In[16]:


# Generate U - Upper bound on the whole VF
def generateU():
    m = Model()
    m.setParam("LogToConsole", 0);
    m.Params.Threads = 1
    
    if mipForU:
        intVarsInit = m.addVars(list(INTVARS), vtype = GRB.INTEGER, lb = 0, ub = UB_I, name = "integer variable")
    else:
        intVarsInit = m.addVars(list(INTVARS), vtype = GRB.CONTINUOUS, lb = 0, ub = UB_I, name = "integer variable")

    contVarsInit = m.addVars(list(CONVARS), vtype = GRB.CONTINUOUS, lb = 0, name = "continuous variable")
    slackVarsInit = m.addVars(list(SLACKVARS), vtype = GRB.CONTINUOUS, lb = 0, name = "slack variable")
    
    m.setObjective(sum(OBJ[i] * intVarsInit[i] for i in INTVARS) + sum(OBJ[i] * contVarsInit[i] for i in CONVARS),
                                                           GRB.MAXIMIZE)
    
    for j in CONSFIXEDRHS:
        m.addConstr(sum(MATFixed[(j, i)] * intVarsInit[i] for i in INTVARS) +
                    sum(MATFixed[(j, i)] * contVarsInit[i] for i in CONVARS) +
                    sum(MATFixed[(j, i)] * slackVarsInit[i] for i in SLACKVARS) == RHS[j])
    m.optimize()
    
    return math.ceil(m.objVal)


# In[17]:


# Generate L - Upper bound on the whole VF
def generateL():
    m = Model()
    m.setParam("LogToConsole", 0);
    m.Params.Threads = 1
    
    if mipForU:
        intVarsInit = m.addVars(list(INTVARS), vtype = GRB.INTEGER, lb = 0, ub = UB_I, name = "integer variable")
    else:
        intVarsInit = m.addVars(list(INTVARS), vtype = GRB.CONTINUOUS, lb = 0, ub = UB_I, name = "integer variable")

    contVarsInit = m.addVars(list(CONVARS), vtype = GRB.CONTINUOUS, lb = 0, name = "continuous variable")
    slackVarsInit = m.addVars(list(SLACKVARS), vtype = GRB.CONTINUOUS, lb = 0, name = "slack variable")
    
    m.setObjective(sum(OBJ[i] * intVarsInit[i] for i in INTVARS) + sum(OBJ[i] * contVarsInit[i] for i in CONVARS),
                                                           GRB.MINIMIZE)
    
    for j in CONSFIXEDRHS:
        m.addConstr(sum(MATFixed[(j, i)] * intVarsInit[i] for i in INTVARS) +
                    sum(MATFixed[(j, i)] * contVarsInit[i] for i in CONVARS) +
                    sum(MATFixed[(j, i)] * slackVarsInit[i] for i in SLACKVARS) == RHS[j])
    m.optimize()
    
    return math.ceil(m.objVal)


# In[18]:


def generateLBZeta(objInd):
    m = Model()
    m.setParam("LogToConsole", 0);
    m.Params.Threads = 1
    
    intVarsInit = m.addVars(list(INTVARS), vtype = GRB.INTEGER, lb = 0, ub = UB_I, name = "integer variable")
    contVarsInit = m.addVars(list(CONVARS), vtype = GRB.CONTINUOUS, lb = 0, name = "continuous variable")
    slackVarsInit = m.addVars(list(SLACKVARS), vtype = GRB.CONTINUOUS, lb = 0, name = "slack variable")
    
    m.setObjective(sum(MAT[(objInd, i)] * intVarsInit[i] for i in INTVARS) + sum(MAT[(objInd, i)] * contVarsInit[i] for i in CONVARS)
                                                                           , GRB.MINIMIZE)
    
    for j in CONSFIXEDRHS:
        m.addConstr(sum(MATFixed[(j, i)] * intVarsInit[i] for i in INTVARS) +
                    sum(MATFixed[(j, i)] * contVarsInit[i] for i in CONVARS) +
                    sum(MATFixed[(j, i)] * slackVarsInit[i] for i in SLACKVARS) == RHS[j])
    m.optimize()

    return m.objVal


# In[19]:


def generateUBZeta(objInd):
    m = Model()
    m.setParam("LogToConsole", 0);
    m.Params.Threads = 1
    
    intVarsInit = m.addVars(list(INTVARS), vtype = GRB.INTEGER, lb = 0, ub = UB_I, name = "integer variable")
    contVarsInit = m.addVars(list(CONVARS), vtype = GRB.CONTINUOUS, lb = 0, name = "continuous variable")
    slackVarsInit = m.addVars(list(SLACKVARS), vtype = GRB.CONTINUOUS, lb = 0, name = "slack variable")
    
    m.setObjective(sum(MAT[(objInd, i)] * intVarsInit[i] for i in INTVARS) + sum(MAT[(objInd, i)] * contVarsInit[i] for i in CONVARS)
                                                                           , GRB.MAXIMIZE)
    
    for j in CONSFIXEDRHS:
        m.addConstr(sum(MATFixed[(j, i)] * intVarsInit[i] for i in INTVARS) +
                    sum(MATFixed[(j, i)] * contVarsInit[i] for i in CONVARS) +
                    sum(MATFixed[(j, i)] * slackVarsInit[i] for i in SLACKVARS) == RHS[j])
    m.optimize()

    return m.objVal


# In[20]:


# Convert the feasible solution to an efficient solution
def convertWeakToStrongNDP(_totalVars, _print=False):
    m = Model()
    m.setParam("LogToConsole", 0);
    m.Params.Threads = 1
    
    intVarsStrong = m.addVars(list(INTVARS), vtype = GRB.INTEGER, lb = 0, ub = UB_I, name = "integer variable")
    contVarsStrong = m.addVars(list(CONVARS), vtype = GRB.CONTINUOUS, lb = 0, name = "continuous variable")
    slackVarsStrong = m.addVars(list(SLACKVARS), vtype = GRB.CONTINUOUS, lb = 0, name = "slack variable")
    
    m.setObjective(sum(OBJ[i] * intVarsStrong[i] for i in INTVARS) + sum(OBJ[i] * contVarsStrong[i] for i in CONVARS) 
                   + sum(MAT[(i, j)] * intVarsStrong[j] for j in INTVARS for i in CONSVARRHS)
                   + sum(MAT[(i, j)] * contVarsStrong[j] for j in CONVARS for i in CONSVARRHS), GRB.MINIMIZE)
    
    RHSFirstObj = 0
    for i in INTVARS:
        RHSFirstObj += OBJ[i] * _totalVars[i]
    for i in CONVARS:
        RHSFirstObj += OBJ[i] * _totalVars[i]
      
    m.addConstr(sum(OBJ[i] * intVarsStrong[i] for i in INTVARS) + sum(OBJ[i] * contVarsStrong[i] for i in CONVARS)
                                                            <= RHSFirstObj)
    
    for j in CONSVARRHS:
        m.addConstr(sum(MAT[(j, i)] * intVarsStrong[i] for i in INTVARS) + 
                    sum(MAT[(j, i)] * contVarsStrong[i] for i in CONVARS) <= 
                    sum(MAT[(j, i)] * _totalVars[i] for i in INTVARS) +
                    sum(MAT[(j, i)] * _totalVars[i] for i in CONVARS))
        
    for j in CONSFIXEDRHS:
        m.addConstr(sum(MATFixed[(j, i)] * intVarsStrong[i] for i in INTVARS) 
                    + sum(MATFixed[(j, i)] * contVarsStrong[i] for i in CONVARS) 
                    + sum(MATFixed[(j, i)] * slackVarsStrong[i] for i in SLACKVARS)  == RHS[j])
    
    m.optimize()

    status = m.getAttr('Status')

    if status in [3, 4]:
        return _totalVars
    
    temp = {}
    for k, v in intVarsStrong.items():
        temp[k] = changeValue(v.X)
    for k, v in contVarsStrong.items():
        temp[k] = changeValue(v.X)
    
    return temp


# In[21]:


# this list will be used to store solutions before conversion
# we will use this list, if necessary to avoid repetitive solutions
intPartList_before_conversions = []


# In[22]:


def RVFSubproblem():
    # use this to check if this round resulted in a new sol
    len_ef_before = len(EF) 
    
    m = Model()
    m.setParam("LogToConsole", 0);
    m.params.NonConvex = 2
    m.Params.Threads = 1
    m.Params.LazyConstraints = 1 # 0 if no lazy is being added, 1 if lazy constraints are being used
    
    # m.setParam('TimeLimit', 60)
    
    # set it to True if you want to use presolve option of gurobi
    presolve = False
    
    if presolve:
        m.Params.Presolve = 2

    if presolve:
        dualLB = -GRB.INFINITY
    else:
        dualLB = -1e20

    thetaVar = m.addVar(vtype = GRB.CONTINUOUS, name = "theta")
    intVars = m.addVars(list(INTVARS), vtype = GRB.INTEGER, lb = 0, ub = UB_I, name = "int_var")
    conVars = m.addVars(list(CONVARS), vtype = GRB.CONTINUOUS, lb = 0, name = "cont_var")
    slackVars = m.addVars(list(SLACKVARS), vtype = GRB.CONTINUOUS, lb = 0, name = "slack_var")
    dualVarsVarRHS = m.addVars(len(CONSVARRHS), len(intPartList), vtype = GRB.CONTINUOUS, lb = dualLB, ub = 0,
                               name = "dual_varying_RHS")
    dualVarsFixedRHS = m.addVars(len(CONSFIXEDRHS), len(intPartList), vtype = GRB.CONTINUOUS, lb = dualLB,
                               name = "dual_fixed_RHS")
            
    m.setObjective(thetaVar, GRB.MAXIMIZE)

    for k in range(len(intPartList)):
        m.addConstr(thetaVar <=
              sum(OBJ[i]*(intPartList[k][i] - intVars[i]) for i in INTVARS)  
            - sum(OBJ[j]*conVars[j] for j in CONVARS)
            + sum(MAT[(i, j)]*dualVarsVarRHS[(i, k)]*(intVars[j] - intPartList[k][j]) for j in INTVARS for i in CONSVARRHS)
            + sum(MAT[(i, j)]*dualVarsVarRHS[(i, k)]*(conVars[j]) for j in CONVARS for i in CONSVARRHS)
            - sum(MATFixed[(i, j)]*dualVarsFixedRHS[(i, k)]*(intPartList[k][j]) for j in INTVARS for i in CONSFIXEDRHS)
            + sum(RHS[i]*dualVarsFixedRHS[(i, k)] for i in CONSFIXEDRHS))

    m.addConstr(thetaVar + sum(OBJ[i]*intVars[i] for i in INTVARS) + sum(OBJ[i]*conVars[i] for i in CONVARS) <= U + 1)

    for k in range(len(intPartList)):
        for j in CONVARS:
            m.addConstr(sum(MAT[(i, j)]*dualVarsVarRHS[(i, k)] for i in CONSVARRHS)
                          + sum(MATFixed[(i, j)]*dualVarsFixedRHS[(i, k)] for i in CONSFIXEDRHS) <= OBJ[j])
    
    for k in range(len(intPartList)):
        for j in SLACKVARS:
            m.addConstr(sum(MATFixed[(i, j)]*dualVarsFixedRHS[(i, k)] for i in CONSFIXEDRHS) <= 0)

    for j in CONSFIXEDRHS:
        m.addConstr(sum(MATFixed[(j, i)] * intVars[i] for i in INTVARS)
                      + sum(MATFixed[(j, i)] * conVars[i] for i in CONVARS)
                      + sum(MATFixed[(j, i)] * slackVars[i] for i in SLACKVARS) == RHS[j])

    m.addConstr(thetaVar >= 1, name = "theta_threshold")

    def my_callback(m, where):
        global len_EF_rvf
    #print(f'test_callback, where= {where}, GRB.Callback.MIPSOL={GRB.Callback.MIPSOL}')
        if where == GRB.Callback.MIPSOL:
            # Get the current solution
            # print('GRB.Callback.MIPSOL', GRB.Callback.MIPSOL)
            
            sol_list = m.cbGetSolution(intVars)
            current_solution = {k: round(sol_list[k]) for k in INTVARS}
            
            # print('current_solution', current_solution)
            # print('int_part_list', intPartList)
            
            sol_list_con = m.cbGetSolution(conVars)
            current_solution_con = {k: round(sol_list_con[k]) for k in CONVARS}

            # first check if current solution is repetitive, if yes add a lazy constraint
            if (current_solution in intPartList_before_conversions) or (current_solution in intPartList):
                # Build lazy constraint to forbid this solution
                expr = LinExpr()
                for j, val in current_solution.items():
                    if round(val) == 1:
                        expr += (1 - intVars[j])
                    else:  # val == 0
                        expr += intVars[j]
                # Add the lazy constraint
                m.cbLazy(expr >= 1)
            else: # the raw solution was not repetitive
                intPartList_before_conversions.append(current_solution)

                # convert it to strong NDP
                total_part_converted = convertWeakToStrongNDP({**current_solution, **current_solution_con}, _print=False)
                current_solution_converted = {k: round(total_part_converted[k]) for k in INTVARS}
                current_solution_con_converted = {k:total_part_converted[k] for k in CONVARS}

                if current_solution_converted in intPartList: # converted solution is repetitive, so lazily remove raw
                    expr = LinExpr()
                    for j, val in current_solution.items():
                        if round(val) == 1:
                            expr += (1 - intVars[j])
                        else:  # val == 0
                            expr += intVars[j]
                    # Add the lazy constraint
                    m.cbLazy(expr >= 1)
                else: # converted solution is not repetitive (ie new solution is found). terminate the B&B            
                    temp_ndp = () 
                    temp_ndp = temp_ndp + (round(sum(OBJ[j]*total_part_converted[j] for j in INTVARS)) +
                                           round(sum(OBJ[j]*total_part_converted[j] for j in CONVARS), 5),)
        
                    for k in CONSVARRHS:
                        temp_ndp = temp_ndp + (round(sum(MAT[(k, l)]*total_part_converted[l] for l in INTVARS)) +
                                               round(sum(MAT[(k, l)]*total_part_converted[l] for l in CONVARS),5),) 
                    
                    len_EF_rvf += 1
                    EF.append(temp_ndp)    
                    intPartList.append({k: round(total_part_converted[k]) for k in INTVARS})
                    contPartList.append({k:total_part_converted[k] for k in CONVARS})
                    m.terminate()
                
    m.optimize(my_callback)
    # print("updated EF:", intPartList)
    # print("after callback")
    
    status = m.getAttr('Status')
    list_num_nodes_rvf.append(m.NodeCount)

    len_ef_after = len(EF) 
    ef_not_changed = (len_ef_after == len_ef_before)

    try:
        thetaVarValue = thetaVar.X
    except Exception: #infeasible cases
        thetaVarValue = 0
    
    if (thetaVarValue < 1) or ef_not_changed:              
        return -1

    return None


# In[23]:


# Generate CRs for each int parts
def generateCR(_int, _sampleZeta):
    m = Model()
    m.setParam("LogToConsole", 0);
    m.Params.Threads = 1

    contVarsInit = m.addVars(list(CONVARS), vtype = GRB.CONTINUOUS, lb = 0, name = "continuous variable")
    slackVarsInit = m.addVars(list(SLACKVARS), vtype = GRB.CONTINUOUS, lb = 0, name = "slack variable")
    
    m.setObjective(sum(OBJ[i] * contVarsInit[i] for i in CONVARS), GRB.MINIMIZE)

    RHS_int = []
    for j in CONSFIXEDRHS:
        RHS_int.append(sum(MATFixed[(j, i)] * _int[i] for i in INTVARS))
    
    for j in CONSFIXEDRHS:
        m.addConstr(sum(MATFixed[(j, i)] * contVarsInit[i] for i in CONVARS) +
                    sum(MATFixed[(j, i)] * slackVarsInit[i] for i in SLACKVARS) == RHS[j] - RHS_int[j])

    RHS_int_var = []
    for j in CONSVARRHS:
        RHS_int_var.append(sum(MAT[(j, i)] * _int[i] for i in INTVARS))
    
    for j in CONSVARRHS:
        m.addConstr(sum(MAT[(j, i)] * contVarsInit[i] for i in CONVARS) <= _sampleZeta[j] - RHS_int_var[j])
        
    m.optimize()
    
    status = m.getAttr('Status')
    if status in [3,4]:
        return U
        
    objValInt = sum(OBJ[i] * _int[i] for i in INTVARS) 
    
    return (m.objVal + objValInt)


# In[24]:


def calcRVFUBAtZeta(sampleZeta):
    UB_temp_lst = []
    for int_parts in intPartList:
        UB_temp_lst.append(generateCR(int_parts, sampleZeta))
        
    return min(UB_temp_lst)


# In[25]:


def calcUBLB(sampleZeta):
    global evalTime
    
    for i in CONSVARRHS:
        RHS_list[i] = sampleZeta[i]
    
    UB_bound = calcRVFUBAtZeta(sampleZeta)

    st_eval = time.time()
    LB_bound = sym.evaluate_dual_function(RHS_list)
    et_eval = time.time()

    evalTime += et_eval - st_eval

    UB_list.append(UB_bound)
    LB_list.append(LB_bound)
    
    if LB_bound == 1e+20:
        gap_list.append(None)
        return UB_bound, None
        
    gap_list.append(UB_bound - LB_bound)
    
    return UB_bound, LB_bound


# In[26]:


minZeta = generateLBZeta(0)
maxZeta = generateUBZeta(0)


# In[27]:


def generate_samples(a, b, n):
    samples = [a]
    interval = (b - a) / (n - 1)
    for i in range(1, n - 1):
        sample = a + i * interval
        samples.append(round(sample,1))
    samples.append(b)
    return samples


# In[28]:


Zeta_LB = []
for i in CONSVARRHS:
    Zeta_LB.append(generateLBZeta(i))

Zeta_UB = []
for i in CONSVARRHS:
    Zeta_UB.append(generateUBZeta(i))

tempListZeta = []

for i in CONSVARRHS:
    tempListZeta.append(generate_samples(Zeta_LB[i], Zeta_UB[i], n_in_sample_size))


tempListZeta = list(itertools.product(*tempListZeta))


# In[29]:


checkDualFunc = False


# In[30]:


# Create SYMPHONY environment
sym = Symphony()
if checkDualFunc:
    sym_rvf = Symphony()


# In[31]:


# Set additional parameters
sym.set_param("verbosity", -2)
sym.set_param("max_active_nodes", 1)

if checkDualFunc:
    sym_rvf.set_param("verbosity", -2)

# Load the problem
sym.read_mps(model_path)

# Load the lp problem
# sym.read_lp(model_path)

if checkDualFunc:
    sym_rvf.read_mps(model_path)

# Enable Warm Start
sym.enable_warm_start()
if checkDualFunc:
    sym_rvf.enable_warm_start()

totalTime = 0
rvfTime = 0
BBTime = 0
buildTime = 0
evalTime = 0

intPartList = []
contPartList = []
EF = []
list_num_nodes_sym = []
list_num_nodes_rvf = []
UB_list = []
LB_list = []
gap_list = []

symIter = 0
RVFIter = 0 
extraIter = 0

feas_status = 0

numNodes = 0

len_EF_sym = 0
len_EF_rvf = 0

RVFCallFrequency  = 100

U = generateU()
L = generateL()


# In[32]:


fixed_RHS_list = list(RHS.values())

RHS_list = []

for i in CONSVARRHS:
    RHS_list.append(0) 

for j in range(len(fixed_RHS_list)):
    RHS_list.append(fixed_RHS_list[j])


# In[33]:


st = time.time()
st_sym = time.time()
if (sym.solve() == FUNCTION_TERMINATED_ABNORMALLY):
    print("Something went wrong!")

list_num_nodes_sym.append(sym.get_tree_size())

symIter += 1

st_sym_build = time.time()
sym.build_dual_function()
et_sym_build = time.time()
buildTime += et_sym_build - st_sym_build

opt_sol = sym.get_col_solution()
if opt_sol:
    # check whether weak solution already exists
    int_part_temp = {k: round(opt_sol[k]) for k in INTVARS}
    if int_part_temp not in intPartList_before_conversions:
        intPartList_before_conversions.append(int_part_temp)
    
        total_part = convertWeakToStrongNDP(opt_sol, _print=False)
        temp_ndp = ()
        temp_ndp = temp_ndp + (round(sum(OBJ[j]*total_part[j] for j in INTVARS)) + round(sum(OBJ[j]*total_part[j] for j in CONVARS)),)
    
        for k in CONSVARRHS: 
            temp_ndp = temp_ndp + (round(sum(MAT[(k, l)]*total_part[l] for l in INTVARS)) + round(sum(MAT[(k, l)]*total_part[l] for l in CONVARS)),)
    
        if temp_ndp not in EF:
            len_EF_sym += 1
            EF.append(temp_ndp)
            intPartList.append({i:round(total_part[i]) for i in INTVARS})
            contPartList.append({i:total_part[i] for i in CONVARS})

et_sym = time.time()

BBTime += et_sym - st_sym


# In[34]:


numLBGRVF = 0
LBGRVFLst = []


# In[35]:


timeSurpassed = False


# In[50]:


# CONSVARRHS


# In[37]:


def runSymphonySubproblem(sample_zeta):
    global len_EF_sym
    global buildTime
   
    for i in CONSVARRHS:
        sym.set_row_upper(i, sample_zeta[i])

    if (sym.warm_solve() == FUNCTION_TERMINATED_ABNORMALLY):
        print("Something went wrong!")

    list_num_nodes_sym.append(sym.get_tree_size() - list_num_nodes_sym[-1])
    
    st_sym_build = time.time()
    sym.build_dual_function()
    et_sym_build = time.time()
    buildTime += et_sym_build - st_sym_build
        
    opt_sol = sym.get_col_solution()
    
    if opt_sol:
        # check whether weak solution already exists
        int_part_temp = {k: round(opt_sol[k]) for k in INTVARS}
        if int_part_temp not in intPartList_before_conversions:
            intPartList_before_conversions.append(int_part_temp)
        
            total_part = convertWeakToStrongNDP(opt_sol, _print=False)
            temp_ndp = ()
            temp_ndp = temp_ndp + (round(sum(OBJ[j]*total_part[j] for j in INTVARS)) + round(sum(OBJ[j]*total_part[j] for j in CONVARS)),)
        
            for k in CONSVARRHS: 
                temp_ndp = temp_ndp + (round(sum(MAT[(k, l)]*total_part[l] for l in INTVARS)) + round(sum(MAT[(k, l)]*total_part[l] for l in CONVARS)),)
    
            if {i: total_part[i] for i in INTVARS} not in intPartList:
                len_EF_sym += 1
                EF.append(temp_ndp)
                # print('EF so far', EF)
                # print('Len EF so far', len(EF))
                # print('Time so far', time.time() - st)
                intPartList.append({i:round(total_part[i]) for i in INTVARS})
                contPartList.append({i:total_part[i] for i in CONVARS})


# In[38]:


# print('main loop starts')
for sample_zeta in tempListZeta:
    # print('---------------------------------------------')
    # print('sample_zeta', sample_zeta)

    UB, LB = calcUBLB(sample_zeta)
    
    if LB == None:
        continue
        
    gap_zeta = UB - LB
            
    if (gap_zeta <= 0.1):
        continue
    
    st_sym = time.time()
    runSymphonySubproblem(sample_zeta)
    et_sym = time.time()
    BBTime += et_sym - st_sym
    
    symIter += 1
    
    if checkDualFunc:
        LB = calcUBLB(sample_zeta)[1]
        
    if checkDualFunc:
        for i in CONSVARRHS:
            sym_rvf.set_row_upper(i, sample_zeta[i])
    
        if (sym_rvf.warm_solve() == FUNCTION_TERMINATED_ABNORMALLY):
            print("Something went wrong!")
        
        opt_sol_rvf = sym_rvf.get_col_solution()
            
        if opt_sol_rvf:
            rvf_val = sym_rvf.get_obj_val()

            if rvf_val + 1 < LB:
                numLBGRVF += 1
                LBGRVFLst.append(sample_zeta)
    
# print('---------------------------------------------')
# print('Main loop ended')
# print('---------------------------------------------')


# In[39]:


# intPartList


# In[40]:


def generate_list_index(input_list):
    output_list = [input_list[0], input_list[-1], input_list[len(input_list)//2]]  # Add first, last, and middle elements
    remaining = set(input_list) - set(output_list)  # Remaining elements to consider

    while remaining:
        sublist_1 = [x for x in remaining if x <= output_list[-1]]  # Elements less than or equal to the last element
        sublist_2 = [x for x in remaining if x > output_list[-1]]   # Elements greater than the last element

        median_1 = sublist_1[len(sublist_1)//2] if sublist_1 else None
        median_2 = sublist_2[len(sublist_2)//2] if sublist_2 else None

        if median_1 is not None:
            output_list.append(median_1)
            remaining.remove(median_1)

        if median_2 is not None:
            output_list.append(median_2)
            remaining.remove(median_2)

    return output_list


# In[41]:


def print_all_logs(_filed_logs, beforeafter='after'):
    _filed_logs.write(str(beforeafter) + ' RVF' + '\n')
    if timeSurpassed:
        _filed_logs.write('Finished due to time limit!' + '\n') 
    else: 
        _filed_logs.write('Finished!' + '\n')  
        
    _filed_logs.write('Total Running Time (sec): ' + str(time.time()-st) + '\n') 
    _filed_logs.write('Total Running Time of RVF (sec): ' + str(rvfTime) + '\n') 

    if RVFIter != 0:
        _filed_logs.write('Avg Running Time of RVF: ' + str(rvfTime/RVFIter) + '\n') 
        
    _filed_logs.write('Total Running Time of BB (sec): ' + str(BBTime) + '\n') 

    if symIter != 0:
        _filed_logs.write('Avg Running Time of BB (sec): ' + str(BBTime/symIter) + '\n') 
        
    _filed_logs.write('Total Running Time of Building Dual Function in BB (sec): ' + str(buildTime) + '\n') 
    _filed_logs.write('Total Running Time of Evaluating Dual Function in BB (sec): ' + str(evalTime) + '\n') 
    _filed_logs.write('List of Number of New Nodes Generated in BB: ' + str(list_num_nodes_sym) + '\n') 
    _filed_logs.write('List of Number of New Nodes Generated in RVF: ' + str(list_num_nodes_rvf) + '\n') 

    if sym.get_tree_size() != 0:
        _filed_logs.write('Avg Running time Per Node in BB: ' + str(BBTime/sym.get_tree_size()) + '\n') 

    if sum(list_num_nodes_rvf) != 0:
        _filed_logs.write('Avg Running time Per Node in RVF: ' + str(rvfTime/sum(list_num_nodes_rvf)) + '\n') 
        
    _filed_logs.write('UB List: ' + str(UB_list) + '\n') 
    _filed_logs.write('LB List: ' + str(LB_list) + '\n') 
    _filed_logs.write('Gap List: ' + str(gap_list) + '\n') 

    if not flag:
        _filed_logs.write('Approximate EF: ' + str(EF) + '\n') 
    else: 
        _filed_logs.write('EF: ' + str(EF) + '\n') 
        
    _filed_logs.write('Number of total NDPs: ' + str(len(EF)) + '\n') 
    _filed_logs.write('Number of iterations of SYMPHONY: ' + str(symIter) + '\n') 
    _filed_logs.write('Number of iterations of RVF: ' + str(RVFIter) + '\n') 
    _filed_logs.write('Number of total iterations: ' + str(symIter + RVFIter) + '\n') 
    _filed_logs.write('Number of NDPs found via SYMPHONY: ' + str(len_EF_sym) + '\n') 
    _filed_logs.write('Number of NDPs found via RVF: ' + str(len_EF_rvf) + '\n') 
    if checkDualFunc:
        _filed_logs.write('Number of cases that LB is greater than RVF: ' + str(numLBGRVF) + '\n') 
        _filed_logs.write('List of zetas that LB is greater than RVF: ' + str(LBGRVFLst) + '\n') 
    _filed_logs.write('Number of Zeta Samples Considered in Symphony: ' + str(len(considered_samples)) + '\n') 
    _filed_logs.write('Number of Total Nodes of the BB: ' + str(sym.get_tree_size()) + '\n')
    _filed_logs.write('Number of Total Nodes of the RVF: ' + str(sum(list_num_nodes_rvf)) + '\n')
    _filed_logs.write('-'*30)
    _filed_logs.flush()


# In[42]:


with open("Results_MILP_multiobj_callback_details_new_{}_{}.txt".format(instance.split('.')[0], initial_sample_size), "a") as _filed_logs:

    flag = False
    
    considered_samples = tempListZeta.copy()
    
    while True:
        if flag:
            break
    
        n_in_sample_size *= 2
    
        tempListZeta = []
        for i in CONSVARRHS:
            tempListZeta.append(generate_samples(Zeta_LB[i], Zeta_UB[i], n_in_sample_size))
    
        tempListZeta = list(itertools.product(*tempListZeta))
    
        tempListZeta = sorted(list(set(tempListZeta) - set(considered_samples)))
        
        desired_list_index = generate_list_index(list(range(len(tempListZeta))))
    
    
        finalListZeta = []
        for _ind in desired_list_index:
            finalListZeta.append(tempListZeta[_ind])
            
        # print('finalListZeta', finalListZeta)
        
        while finalListZeta: 
            # print('---------------------------------------------')
            # print('inside third loop')
            # print('finalListZeta: ', finalListZeta)
            # print('extraIter: ', extraIter)
        
            if extraIter % RVFCallFrequency == 0:
                extraIter += 1
                # print('rvf loop')
                # print('RVF is called')
                # print(f'len EF before: {len(EF)}, EF: {EF}')
                len_ef_before = len(EF) #bugfix
                st_rvf = time.time()

                print_all_logs(_filed_logs, beforeafter='before')
                
                feas_status = RVFSubproblem()
                print_all_logs(_filed_logs) #temporarily print all
                
                et_rvf = time.time()
                # print(f'len EF after: {len(EF)}, EF: {EF}')
                len_ef_after = len(EF) #bugfix
    
                rvfTime += et_rvf - st_rvf
                
                RVFIter += 1
                if (feas_status == -1) or (len_ef_after == len_ef_before):
                    print('Reached to optimality!')
                    flag = True
                    break
                
            else:
                extraIter += 1
                
                sample_zeta = finalListZeta[0]
                finalListZeta = finalListZeta[1:]

                UB, LB = calcUBLB(sample_zeta)

                if LB == None:
                    continue
                    
                gap_zeta = UB - LB
                if (gap_zeta <= 0.1):
                    continue
                    
                considered_samples.append(sample_zeta)
                st_sym = time.time()
                runSymphonySubproblem(sample_zeta)
                et_sym = time.time()
                BBTime += et_sym - st_sym
                
                symIter += 1
            
            et = time.time()
            totalTime = et - st
    
        et = time.time()
        totalTime = et - st 
            
        if totalTime > timeLimit:
            timeSurpassed = True
            break 
    
    et = time.time()
    totalTime = et - st 


# In[54]:


# if timeSurpassed:
#     print("Finished due to time limit!")
# else: 
#     print("Finished!")

# print('Total Running Time (sec): ', totalTime)
# print('Total Running Time of RVF (sec): ', rvfTime)

# if RVFIter != 0:
#     print('Avg Running Time of RVF (sec): ', rvfTime/RVFIter)
    
# print('Total Running Time of BB (sec): ', BBTime)

# if symIter != 0:
#     print('Avg Running Time of BB (sec): ', BBTime/symIter)
    
# print('Total Running Time of Building Dual Function in BB (sec): ', buildTime)
# print('Total Running Time of Evaluating Dual Function in BB (sec): ', evalTime)
# print('List of Number of New Nodes Generated in BB: ', list_num_nodes_sym)
# print('List of Number of New Nodes Generated in RVF: ', list_num_nodes_rvf)

# if sym.get_tree_size() != 0:
#     print('Avg Running time Per Node in BB: ', BBTime/sym.get_tree_size())

# if sum(list_num_nodes_rvf) != 0:
#     print('Avg Running time Per Node in RVF: ', rvfTime/sum(list_num_nodes_rvf))
    
# print('\n')
# print('UB List: ', UB_list)
# print('\n')
# print('LB List: ', LB_list)
# print('\n')
# print('Gap List: ', gap_list)

# print('\n')

# if not flag:
#     print('Approximate EF: ' , EF)
# else: 
#     print('EF: ' , EF)

# print('\n')

# print('Number of total NDPs: ', len(EF))
# print('Number of iterations of SYMPHONY: ', symIter)
# print('Number of iterations of RVF: ', RVFIter)
# print('Number of total iterations: ', symIter + RVFIter)
# print('Number of NDPs found via SYMPHONY: ', len_EF_sym)
# print('Number of NDPs found via RVF: ', len_EF_rvf)
# if checkDualFunc:
#     print('Number of cases that LB is greater than RVF: ', numLBGRVF)
#     print('List of zetas that LB is greater than RVF: ', LBGRVFLst)
# print('Number of Zeta Samples Considered in Symphony: ', len(considered_samples))
# print('Number of Total Nodes of the BB: ', sym.get_tree_size())
# print('Number of Total Nodes of the RVF: ', sum(list_num_nodes_rvf))


# In[51]:


# EF


# In[52]:


# len(EF)


# In[53]:


# intPartList


# In[47]:


with open("Results_MILP_multiobj_callback_details_{}_{}.txt".format(instance.split('.')[0], initial_sample_size), "a") as _filed:
    if timeSurpassed:
        _filed.write('Finished due to time limit!' + '\n') 
    else: 
        _filed.write('Finished!' + '\n')  
        
    _filed.write('Total Running Time (sec): ' + str(totalTime) + '\n') 
    _filed.write('Total Running Time of RVF (sec): ' + str(rvfTime) + '\n') 

    if RVFIter != 0:
        _filed.write('Avg Running Time of RVF: ' + str(rvfTime/RVFIter) + '\n') 
        
    _filed.write('Total Running Time of BB (sec): ' + str(BBTime) + '\n') 

    if symIter != 0:
        _filed.write('Avg Running Time of BB (sec): ' + str(BBTime/symIter) + '\n') 
        
    _filed.write('Total Running Time of Building Dual Function in BB (sec): ' + str(buildTime) + '\n') 
    _filed.write('Total Running Time of Evaluating Dual Function in BB (sec): ' + str(evalTime) + '\n') 
    _filed.write('List of Number of New Nodes Generated in BB: ' + str(list_num_nodes_sym) + '\n') 
    _filed.write('List of Number of New Nodes Generated in RVF: ' + str(list_num_nodes_rvf) + '\n') 

    if sym.get_tree_size() != 0:
        _filed.write('Avg Running time Per Node in BB: ' + str(BBTime/sym.get_tree_size()) + '\n') 

    if sum(list_num_nodes_rvf) != 0:
        _filed.write('Avg Running time Per Node in RVF: ' + str(rvfTime/sum(list_num_nodes_rvf)) + '\n') 
        
    _filed.write('UB List: ' + str(UB_list) + '\n') 
    _filed.write('LB List: ' + str(LB_list) + '\n') 
    _filed.write('Gap List: ' + str(gap_list) + '\n') 

    if not flag:
        _filed.write('Approximate EF: ' + str(EF) + '\n') 
    else: 
        _filed.write('EF: ' + str(EF) + '\n') 
        
    _filed.write('Number of total NDPs: ' + str(len(EF)) + '\n') 
    _filed.write('Number of iterations of SYMPHONY: ' + str(symIter) + '\n') 
    _filed.write('Number of iterations of RVF: ' + str(RVFIter) + '\n') 
    _filed.write('Number of total iterations: ' + str(symIter + RVFIter) + '\n') 
    _filed.write('Number of NDPs found via SYMPHONY: ' + str(len_EF_sym) + '\n') 
    _filed.write('Number of NDPs found via RVF: ' + str(len_EF_rvf) + '\n') 
    if checkDualFunc:
        _filed.write('Number of cases that LB is greater than RVF: ' + str(numLBGRVF) + '\n') 
        _filed.write('List of zetas that LB is greater than RVF: ' + str(LBGRVFLst) + '\n') 
    _filed.write('Number of Zeta Samples Considered in Symphony: ' + str(len(considered_samples)) + '\n') 
    _filed.write('Number of Total Nodes of the BB: ' + str(sym.get_tree_size()) + '\n')
    _filed.write('Number of Total Nodes of the RVF: ' + str(sum(list_num_nodes_rvf)))


# In[48]:


del sym


# In[49]:


if checkDualFunc:
    del sym_rvf


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




