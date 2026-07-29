using Statistics
using Plots

struct DataPoint
    x::Float64
    y::Float64
    label::String
end

function analyze_data(points::Vector{DataPoint})::Dict{String, Any}
    values = [p.y for p in points]

    stats = Dict(
        "mean" => mean(values),
        "std" => std(values),
        "min" => minimum(values),
        "max" => maximum(values)
    )

    @info "Analyzed $(length(points)) data points"

    return stats
end

data = [DataPoint(i, sin(i * π / 10), "point_$i") for i in 1:10]
results = analyze_data(data)
println("Statistics: $(results["mean"])")
