using ArgParse

function parse_commandline()
    s = ArgParseSettings()

    @add_arg_table! s begin
        "--instance"
            help = "specify the instance"
        "--method"
            help = "choose the multi-objective method (numeric code)"
            arg_type = Int
            default = 1
        "--timelimit"
            help = "set a time limit in seconds (optional)"
            arg_type = Float64
            default = -1.0
    end

    return parse_args(s)
end

parsed_args = parse_commandline()

loc = parsed_args["instance"] 
content = open(loc) do file
    read(file, String)
end

using JuMP
using HiGHS
using LinearAlgebra
import MathOptInterface as MOI
import MultiObjectiveAlgorithms as MOA

cont = split(content, "\n")
cont = [strip(i) for i in cont if strip(i) != ""]

# First line: number of objectives
numObj = parse(Int64, cont[1])

# Second line: number of variables
numVar = parse(Int64, cont[2])

# Third line: knapsack capacity
capacity = parse(Int64, cont[3])

# Next numObj lines: objective coefficients
p = [
    [parse(Int64, replace(j, ['[', ']'] => "")) for j in split(cont[3+i], ",") if strip(j) != ""]
    for i in 1:numObj
]

# Last line: constraint coefficients (weights)
weights = [parse(Int64, replace(j, ['[', ']'] => "")) for j in split(cont[end], ",") if strip(j) != ""]

# -----------------------
# Build JuMP model
# -----------------------
t1 = time_ns()

m = JuMP.Model(() -> MOA.Optimizer(HiGHS.Optimizer))
#set_silent(m)

@variable(m, x[1:numVar], Bin)

# Build objectives as expressions
objs = [dot(x, p[i]) for i in 1:numObj]

# Multi-objective
@objective(m, Max, objs)

# Single knapsack constraint
@constraint(m, sum(weights[j] * x[j] for j=1:numVar) <= capacity)

# -----------------------
# Multi-objective solver setup
# -----------------------
if parsed_args["method"] == 1
    println("MOA.TambyVanderpooten()")
    set_attribute(m, MOA.Algorithm(), MOA.TambyVanderpooten())
elseif parsed_args["method"] == 2
    println("MOA.KirlikSayin()")
    set_attribute(m, MOA.Algorithm(), MOA.KirlikSayin())
elseif parsed_args["method"] == 3
    println("MOA.DominguezRios()")
    set_attribute(m, MOA.Algorithm(), MOA.DominguezRios())
elseif parsed_args["method"] == 4
    println("MOA.EpsilonConstraint()")
    set_attribute(m, MOA.Algorithm(), MOA.EpsilonConstraint())
elseif parsed_args["method"] == 5
    println("MOA.Chalmet()")
    set_attribute(m, MOA.Algorithm(), MOA.Chalmet())
else
    error("Unknown method code. Use 1-5.")
end

# DominguezRios >=2 Minimum complete set
# KirlikSayin >=2 Minimum complete set
# TambyVanderpooten >=2 Minimum complete set

# ---not useful
# Chalmet ==2 Minimum complete set
# EpsilonConstraint ==2 Minimum complete set
# Dichotomy ==2 Minimum supported set ---not useful
# Sandwiching >=2 Minimum supported set ---not useful

# -------------------------
# Set a time limit
# -------------------------
if parsed_args["timelimit"] > 0.0
   println("Setting time limit to ", parsed_args["timelimit"], " seconds.")
   set_time_limit_sec(m, parsed_args["timelimit"])
end

set_attribute(m, MOA.ComputeIdealPoint(), false)

println("Elapsed Time before solve: ", (time_ns() - t1) / 1.0e9, " seconds")
flush(stdout)

# -----------------------
# Solve
# -----------------------
optimize!(m)

# -----------------------
# Collect results
# -----------------------
for i in 1:result_count(m)
    xv = value.(x; result = i)
    z  = objective_value(m; result = i)
    println("Solution $i: x indices = ", findall(v -> v ≈ 1, xv), " | z = ", z)
end

t2 = time_ns()
elapsedTime = (t2 - t1) / 1.0e9
println("Elapsed Time: ", elapsedTime, " seconds")

println(solution_summary(m))
