from math import e
import sys, os, collections
import shutil, subprocess, itertools

sys.path.append("..")

import numpy as np
import pandas as pd
from parameters import versions, outputDir, instanceDirs, symParams

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import rcParams
rcParams["mathtext.fontset"] = 'cm'
plt.rcParams['text.usetex'] = True


def parseOutput(outputDir, versions, scenarios, writeCSV=True, filename="summary.csv"):
    keywords = {
            "incomplete" : "Forest Statistics",
            "solved" : "Reached to optimality!",
            "cpu" : "Total Running Time (sec):",
            "cpu_rvf" : "Total Running Time RVFiter (sec):",
            "cpu_bb" : "Total Running Time BBiter (sec):",
            "cpu_vopt" : "Elapsed Time:",
            "num_ndps" : "Number of total NDPs:",
            "iter_count" : "Number of total iterations:",
        "num_int_vars" : "Integer:",
        "num_cont_vars" : "Continuous:",
            "num_constr" : "Total number of constraints:",
            "num_objs" : "Total number of objectives:",
            "num_trees" : "Total number of trees:"
    }

    results = collections.defaultdict(list)

    for v in versions:
        for testset in instanceDirs:
            for scenario in scenarios:
                currpath = os.path.join(outputDir, v, scenario, testset)
                with os.scandir(currpath) as inst_it: 
                    for instance in inst_it:
    #                     print(instance.name)
                        if instance.name.lower().endswith('.out'):
                            results["dataset"].append(testset)
                            results["scenario"].append(scenarios[scenario])
                            results["version"].append(v)
                            results["instance"].append(os.path.splitext(instance.name)[0])
                            # Set some defaults
                            results['incomplete'].append(True)
                            results['solved'].append(False)
                            results["cpu"].append(3600)
                            results["num_ndps"].append(0)
                            results["iter_count"].append(0)
                            results["num_int_vars"].append(0)
                            results["num_cont_vars"].append(0)
                            results["num_constr"].append(0)
                            results["num_objs"].append(0)
                            results["num_trees"].append(0)

                            # read value for each field from file
                            with open(instance.path, "r") as file:
                                for line in file.read().splitlines():
                                    if keywords["cpu"] in line:
                                        results["cpu"][-1] = (float(line.split()[-1]))

                                    elif keywords["incomplete"] in line:
                                        results["incomplete"][-1] = False
                                    
                                    elif keywords["solved"] in line:
                                        results["solved"][-1] = True
                                        
                                    elif keywords["num_ndps"] in line:
                                        results["num_ndps"][-1] = (int(line.split()[-1]))
                                        
                                    elif keywords["iter_count"] in line:
                                        results["iter_count"][-1] = (int(line.split()[-1]))
                                    
                                    elif keywords["num_int_vars"] in line:
                                        results["num_int_vars"][-1] = (int(line.split()[-1]))
                                    
                                    elif keywords["num_cont_vars"] in line:
                                        results["num_cont_vars"][-1] = (int(line.split()[-1]))
                                    
                                    elif keywords["num_constr"] in line:
                                        results["num_constr"][-1] = (int(line.split()[-1]))
                                    
                                    elif keywords["num_objs"] in line:
                                        results["num_objs"][-1] = (int(line.split()[-1]))

                                    elif keywords["num_trees"] in line:
                                        results["num_trees"][-1] = (int(line.split()[-1]))
                                    
                                    # vOpt
                                    if keywords["cpu_vopt"] in line:
                                        results["cpu"][-1] = (float(line.split()[-2]))

                            # compute derived values
                            results["num_vars"].append(results["num_int_vars"][-1] + results["num_cont_vars"][-1])
                            results["num_vars_constr"].append(results["num_vars"][-1] + results["num_constr"][-1])

    df = pd.DataFrame(results)

    print(df)

    # write results to .csv file
    if writeCSV:
        # df_result.to_csv(filename, mode='a', header=False, index=False) # append results only
        df.to_csv(filename, index=False)

    return df


def processTable(df, displayCols, writeLTX=False, filename="ltx_tb.txt"):
    """
    Print a summary table for required columns.
    Input:
        df: a dataframe with all info from parseOutput
        displayCol: columns to print
    """

    # separate instance to different tables
    # convert each instance related data into a dictionary
    # each data field can print to a table
    # or print a summary table where instance by row

    # obtain the list of instances
    instList = list(df.instance.unique())
    scnList = list(df.scenario.unique())
    versionList = list(df.version.unique())
    # print(instList)

    # collect required info into dict
    rsltDict = {}
    for inst in instList:
        rsltDict[inst] = {}

        for scn in scnList:
            for v in versionList:
                cond = (
                    (df["scenario"] == scn)
                    & (df["instance"] == inst)
                    & (df["version"] == v)
                )
                df_temp = df[cond]
                if len(df_temp["dataset"].values) > 0:
                    ds = df_temp["dataset"].values[0]
                    rsltDict[inst].update(
                        {(scn, v, ds, col): df_temp[col].values[0] for col in displayCols}
                )
                    rsltDict[inst].update(
                        {(scn, v, 'all', col): df_temp[col].values[0] for col in displayCols}
                )

    # convert dict to structured df: change to formal column names?
    df_forprint = pd.DataFrame.from_dict(rsltDict, orient="index")
    df_forprint.columns.names = ["scn", "v", "datasets", "fields"]
    # df_forprint = df_forprint.sort_index()

    # OPTION 1: print results to a single table: suggest to use when display col number < 2
    # with open('ltx_tb1.txt', 'w') as file:
    #     file.write(df_forprint.to_latex())

    # OPTION 2: for each displayCol, print a table; using slicer indexing
    if writeLTX:
        with open(filename, "w") as file:
            for col in displayCols:
                for scn in scnList:
                    file.write(df_forprint.loc[:, (scn, slice(None), col)].to_latex())

    # OPTION 3: just process table, do not print latex table to file
    # pass

    return df_forprint


def dropFilter(df, scenarios, ds):
    """
    Prepare data for plotting performance profile; running time only.
    Input:
        df: pandas dataframe output from processTable
        plotCol: columns to make single plots
        scenarios: scenarios on one plot
    """
    df = df[scenarios.values()]
    # replace unsolved cases by a large number
    for scn in df.columns:
        df[scn] = pd.to_numeric(df[scn], errors="coerce").replace(np.nan, 1e11)
    # apply index filter on solution time
    df_time = df.xs(
        (ds, "cpu"), level=["datasets", "fields"], axis=1, drop_level=True
    ).copy()
    df_solved = df.xs(
        (ds, "solved"), level=["datasets", "fields"], axis=1, drop_level=True
    ).copy()
    # df_time = pd.to_numeric(df_time, errors='coerce').replace(np.nan, 36000)
    # filter out cases where time is < 5'' or > 3600'' for all methods
    col_list = df_time.columns.values.tolist()

    drop_easy = df_time[(df_time[col_list] < 1).all(axis=1)].index.tolist()
    drop_small_time = df_time[(df_time[col_list] <= 0.01).any(axis=1)].index.tolist()
    drop_unsolved = df_solved[(df_solved[col_list] != True).all(axis=1)].index.tolist()
    drop_list_time = list(set(drop_easy) | set(drop_unsolved) | set(drop_small_time))
    #drop_list_time.extend(["cap6000-0.100000","cap6000-0.500000","cap6000-0.900000"])
    #print(drop_easy)
    #print(drop_small_time)
    #print(drop_unsolved)
    df_solved = df.drop(drop_list_time)

    return df_solved


def plotPerfProf(
        df, plotname="perf_profile", plottitle="Performance Profile", plotformat='png',
        xmin=0.0, xmax=None, legendnames={}, versionlegend=False
):
    """
    Generate a performance profile plot for the given dataframe.
    Assume data given are in number types.
    x-axis label: multiple of virtual best;
    y-axis label: franction of instances.
    Input:
        df: instances as index, field-to-plot as columns
        plotname: name of the plot
        fixmin: the base value used to compute ratio; using df min if not given
        xmin: the smallest x-ticker to display; set by xlim
        xmax: the largest x-ticker to display; set by xlim
        displaynames: a dictionary contains legend name; using df col name if not given
    """

    num_lines = len(scenarios)
    cmap = cm.get_cmap(colorPalette, num_lines)
    i = 0

    fig, ax = plt.subplots(1, 1)

    # if given legend name len != col #, use defualt column name
    if legendnames and (len(legendnames) != len(df.columns)):
        legendnames = {}

    # find min value in the dataframe
    col_list = df.columns.values.tolist()
    df["virtual_best"] = df[col_list].min(axis=1)

    #print(df["virtual_best"])
    
    for col in col_list:
        # print(col_list)
        # print(col)
        # for each col, compute ratio
        ratios = df[col] / df["virtual_best"]
        with pd.option_context('display.max_rows', None,
                              'display.max_columns', None,
                              'display.precision', 3,
        ):
            print(df[col])
        #    print(ratios.sort_values())
        #    print(ratios)
        uniq_ratios = ratios.unique()
        uniq_ratios.sort()  # sort in place

        #print(uniq_ratios)
        cum_cnt = np.sum(np.array([ratios <= ur for ur in uniq_ratios]), axis=1)
        cum_frac = cum_cnt / len(ratios)
        #print(cum_frac)

        # form x-tickers: if xmax is not given, use current max and round up
        if xmax == None:
            xmax = np.ceil(uniq_ratios[-1])
        elif uniq_ratios[-1] < xmax:
            np.append(uniq_ratios, xmax)  # append array at the boundary point
            np.append(cum_frac, cum_frac[-1])

        # add turning points and form series to plot
        x_val = []
        y_val = []
        x_val.append(1.0)
        y_val.append(0.0)
        if uniq_ratios[0] > 1:
            x_val.append(uniq_ratios[0])
            y_val.append(0)
        x_val.append(uniq_ratios[0])
        y_val.append(cum_frac[0])
        for j, r in enumerate(uniq_ratios[1:]):
            x_val.extend([r, r])
            y_val.extend([cum_frac[j], cum_frac[j + 1]])
            #print(r, cum_frac[j])
            #print(r, cum_frac[j+1])
        if cum_frac[-1] == 1.0:
            x_val.append(xmax)
            y_val.append(1.0)

        if legendnames:
            # , color=colors[i])
            plt.plot(x_val, y_val, label=legendnames[col], color=cmap(i))
        elif versionlegend:
            plt.plot(x_val, y_val, label=col, color=cmap(i))  # , color=colors[i])
        else:
            plt.plot(x_val, y_val, label=col[0], color=cmap(i))  # , color=colors[i])
        i += 1

    # set plot properties
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(-0.02, 1.05)
    ax.tick_params(axis="both", direction="in", right=True)

    # set other figure elements
    ax.set_title(plottitle)
    ax.set_xlabel("Multiple of virtual best")
    ax.set_ylabel("Fraction of instances")
    ax.legend(
        loc="lower right",
        #bbox_to_anchor=(0.9, 0.9),
        markerscale=1.25,
        frameon=True,
        labelspacing=0.35,
        fontsize="x-small",
    )

    fig.tight_layout()
    fig.savefig(plotname + '.' + plotformat, dpi=fig.dpi)

def plotBaselineProf(
        df, baseline, plotname="base_profile", plottitle="Baseline Profile", plotformat='png',
        xmin=0.0, xmax=None, legendnames={}, versionlegend=False
):
    """
    Generate a performance profile plot for the given dataframe.
    Assume data given are in number types.
    x-axis label: multiple of virtual best;
    y-axis label: franction of instances.
    Input:
        df: instances as index, field-to-plot as columns
        plotname: name of the plot
        fixmin: the base value used to compute ratio; using df min if not given
        xmin: the smallest x-ticker to display; set by xlim
        xmax: the largest x-ticker to display; set by xlim
        displaynames: a dictionary contains legend name; using df col name if not given
    """

    num_lines = len(scenarios) - 1
    cmap = cm.get_cmap(colorPalette, num_lines)
    i = 0

    fig = plt.figure()
    gs = fig.add_gridspec(1, 2, wspace=0)
    ax = gs.subplots(sharey=True)

    # if given legend name len != col #, use defualt column name
    if legendnames and (len(legendnames) != len(df.columns)):
        legendnames = {}

    # find min value in the dataframe
    col_list = df.columns.values.tolist()

    for col in col_list:
        if col == baseline or col[0] == "virtual_best":
            continue
        #print(col)
        # for each col, compute ratio
        ratios = df[col] / df[baseline]
        #print(df[col])
        uniq_ratios = ratios.unique()
        uniq_ratios.sort()  # sort in place
        #print(uniq_ratios)

        cum_cnt = np.sum(np.array([ratios <= ur for ur in uniq_ratios]), axis=1)
        cum_frac = cum_cnt / len(ratios)

        # form x-tickers: if xmax is not given, use current max and round up
        if xmax == None:
            xmax = np.ceil(uniq_ratios[-1])
        elif uniq_ratios[-1] < xmax:
            uniq_ratios = np.append(uniq_ratios, xmax)  # append array at the boundary point
            cum_frac = np.append(cum_frac, cum_frac[-1])

        #print(cum_frac)

        # Values less than one are scaled differently
        if uniq_ratios[0] < 1:
            x_val = []
            y_val = []
            x_val.append(0.0)
            y_val.append(0.0)
            x_val.append(uniq_ratios[0])
            y_val.append(0)
            x_val.append(uniq_ratios[0])
            y_val.append(cum_frac[0])
            for j, r in enumerate(uniq_ratios[1:]):
                if r > 1:
                    x_val.append(r)
                    y_val.append(cum_frac[j])
                    break
                x_val.extend([r, r])
                # j is indexed starting at zero, not one!
                y_val.extend([cum_frac[j], cum_frac[j + 1]])

            if legendnames:
                # , color=colors[i])
                ax[0].plot(x_val, y_val, label=legendnames[col], color=cmap(i))
            elif versionlegend:
                ax[0].plot(x_val, y_val, label=col, color=cmap(i))  # , color=colors[i])
            else:
                ax[0].plot(x_val, y_val, label=col[0], color=cmap(i))  # , color=colors[i])

        # add turning points and form series to plot
        x_val = []
        y_val = []
        if uniq_ratios[0] >= 1:
            x_val.append(1.0)
            y_val.append(0.0)
            j = 0
        if uniq_ratios[0] > 1:
            x_val.append(uniq_ratios[0])
            y_val.append(0)
        x_val.append(uniq_ratios[j])
        y_val.append(cum_frac[j])
        
        for k, r in enumerate(uniq_ratios[j+1:]):
            x_val.extend([r, r])
            y_val.extend([cum_frac[k+j], cum_frac[k+j+1]])

        if legendnames:
            # , color=colors[i])
            ax[1].plot(x_val, y_val, label=legendnames[col], color=cmap(i))
        elif versionlegend:
            ax[1].plot(x_val, y_val, label=col, color=cmap(i))  # , color=colors[i])
        else:
            ax[1].plot(x_val, y_val, label=col[0], color=cmap(i))  # , color=colors[i])
        i += 1

    # set plot properties
    ax[0].set_xlim(0, 1)
    ax[0].set_ylim(-0.02, 1.05)
    ax[0].tick_params(axis="both", direction="in", right=True)

    ax[1].set_xlim(1, xmax)
    ax[1].label_outer()
    ax[1].tick_params(axis="both", direction="in", right=True)
    ax[1].legend(
        loc="lower right",
        #bbox_to_anchor=(0.9, 0.05),
        markerscale=1.25,
        frameon=True,
        labelspacing=0.35,
        fontsize="x-small",
    )

    fig.supxlabel("Ratio of baseline (%s)" % baseline[0])
    fig.supylabel("Fraction of instances")
    fig.suptitle(plottitle)
    fig.tight_layout()
    fig.savefig(plotname + '.' + plotformat, dpi=fig.dpi)

if __name__ == "__main__":
    # Scenarios
    #     keys: correspond to the keys of mibsParamsInputs in parameters.py
    #     values: is the name to use in plots
    scenarios = {
        'forest_warmstart' : 'Warm_Start',
        'forest_coldstart' : 'Cold_Start',
        'forest_hybrid' : 'Hybrid',
        'vOpt' : 'MOA',
        # 'forest_warmstart_SAMPLE50' : 'Warm_Start_50',
        # 'forest_warmstart_SAMPLE100' : 'Warm_Start_100',
        # 'forest_warmstart_SAMPLE300' : 'Warm_Start_300',
        # 'forest_coldstart_SAMPLE50' : 'Cold_Start_50',
        # 'forest_coldstart_SAMPLE100' : 'Cold_Start_100',
        # 'forest_coldstart_SAMPLE300' : 'Cold_Start_300',
        # 'forest_hybrid_SAMPLE50' : 'Hybrid_50',
        # 'forest_hybrid_SAMPLE100' : 'Hybrid_100',
        # 'forest_hybrid_SAMPLE300' : 'Hybrid_300'
    }
    df = parseOutput(outputDir, versions, scenarios)

    # Columns to process and print
    displayCols = {
        'incomplete' : 'Incomplete',
        'solved' : 'Solved',
        'cpu' : 'CPU Time',
        'num_ndps' : 'Num NDPs',
        'iter_count' : 'Num Iterations',
        'num_int_vars' : 'Num Int Vars',
        'num_cont_vars' : 'Num Cont Vars',
        'num_vars' : 'Num Vars',
        'num_constr' : 'Num Constr',
        'num_vars_constr' : 'Num Vars + Constr',
        'num_objs' : 'Num Objectives',
        'num_trees' : 'Num Trees'
    }

    # Columns to plot
    plotCols = {
        "cpu": ["CPU Time", 10]
        # "cpu": ["CPU Time", 4]
    }

    baseline = None
    baseline = ("MOA", "forest")
    # baseline = ("Cold_Start", "forest")
    # baseline = ("Hybrid", "forest")
    # baseline = ("Warm_Start", "forest")

    dataSets = ['all']

    ds_name = "KP_SPP"

    if len(versions) > 1:
        versionlegend = True
    else:
        versionlegend = False

    colorPalette = 'tab20'
    plotformat = 'pdf' # 'png'


    df_proc = processTable(df, displayCols)
    
    for ds in dataSets:
        df_solved = dropFilter(df_proc, scenarios, ds)
        # print(df_solved)
        for col in plotCols:
            
            df_sub = df_solved.xs(
                (ds, col), level=["datasets", "fields"], axis=1, drop_level=True
            ).copy()
            
            print("")
            print("Creating performance profile for " + col , ", num instances: ", len(df_sub))
            print("")
            plotPerfProf(
                df_sub, plotname=("perf_" + col + "_" + ds_name).replace(' ', '_'),
                plottitle = "Performance Profile: "+plotCols[col][0]+" ("+ds_name+")",
                xmin = 0.0, xmax=plotCols[col][1],
                versionlegend = versionlegend, plotformat=plotformat
            )

            if baseline is not None: 
                print("")
                print("Creating baseline profile for "+col)
                print("")
                plotBaselineProf(
                    df_sub, baseline = baseline,
                    plotname=("base_"+baseline[0]+"_"+col+"_"+ds_name).replace(' ', '_'),
                    plottitle = "Baseline Profile: "+plotCols[col][0]+" ("+ds_name+")",
                    xmax=plotCols[col][1],
                    versionlegend = versionlegend, plotformat=plotformat
                )



# print(df[df['num_objs'] == 2][['instance', 'num_objs', 'num_vars', "num_vars_constr", 'cpu']])


# filename = "KP_SSP_momilp_results.pdf"

# fig, ax = plt.subplots(figsize=(8, 6))

# # Define marker styles (cycling through them if there are more unique datasets)
# markers = itertools.cycle(['o', '^', 'v', 'D', 's', 'p', '*', 'X'])  
# unique_datasets = df["dataset"].unique()

# # Normalize colors for num_objs
# num_objs_unique = np.sort(df["num_objs"].unique())
# norm = plt.Normalize(vmin=num_objs_unique.min(), vmax=num_objs_unique.max())
# cmap = plt.cm.viridis

# scatters = []
# legend_handles = []

# # Scatter plot with different markers and colors
# for dataset, marker in zip(unique_datasets, markers):
#     subset = df[df["dataset"] == dataset]
#     sc = ax.scatter(
#         subset["num_vars_constr"], 
#         subset["cpu"], 
#         c=subset["num_objs"], 
#         cmap=cmap, 
#         norm=norm,
#         alpha=0.75, 
#         marker=marker, 
#         label=dataset  # Add dataset to legend
#     )
#     scatters.append(sc)
#     # Create black markers for the legend
#     legend_handles.append(plt.Line2D([0], [0], marker=marker, color='black', linestyle='', markersize=8, label=dataset))

# ax.set_yscale("log")  # Log scale for y-axis
# ax.set_xscale("log")  # Log scale for x-axis
# ax.set_xlabel("Number of Variables + Constraints", fontsize=17)
# ax.set_ylabel("Total Runtime (sec.)", fontsize=17)
# # ax.set_title("Scatter Plot of Total Runtime vs. Num Vars/Constr")

# # Add color bar for num_objs
# cbar = plt.colorbar(scatters[0], ax=ax)
# cbar.set_label("Number of Parametric Constraints", fontsize=17)

# # Force colorbar to show only integer values
# cbar.set_ticks(num_objs_unique)
# cbar.set_ticklabels(map(str, num_objs_unique))

# # Show grid only on y-axis
# ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.5)

# # Add legend for dataset markers in black
# ax.legend(handles=legend_handles, title="Dataset", loc="best")


# plt.savefig(filename)
# # plt.show()