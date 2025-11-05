# Script to set up parameters for SYMPHONY

# Absolute path to the libSym, extention change based on the OS:
# - Windows: .dll
# - Linux: .so
# - OSX: .dylib
lib_path = r'/Users/feb223/projects/coin/RVF/build-SYM-opt/lib/libSym.dylib'

# SYMPHONY version
versions = ['forest']

# Output parent path
outputDir = '../tests'

# Instance path
# Directory name and path containing test instances in .mps format
# Keys are used to name subdirs in output dir
instanceDirs = {
    'KP' : '../data/KP',
    # 'SPP' : '../data/SPP',
    #  'MILP' : '../data/MILP',
    #   'smallMILP' : '../data/smallMILP'
}

# Set up senarios
commonParams = {
     'timelimit' : '3600',
    #  'frequencyrvf' : '50'
}
# SYMPHONY additional parameters to be set
symParams = {
    
}


# Sample size: 20 for biobjs and 80 for multiobjs
symParams['forest_warmstart'] = {
    'policy' : '0'
}

symParams['forest_coldstart'] = {
    'policy' : '1'
}

symParams['forest_hybrid'] = {
    'policy' : '2'
}

symParams['vOpt'] = {
}

# symParams['forest_warmstart_SAMPLE50_FREQ50'] = {
#     'policy' : '0',
#     'samples' : '50'
# }

# symParams['forest_coldstart_SAMPLE50_FREQ50'] = {
#     'policy' : '1',
#     'samples' : '50'
# }

# symParams['forest_hybrid_SAMPLE50_FREQ50'] = {
#     'policy' : '2',
#     'samples' : '50'
# }


# symParams['forest_warmstart_SAMPLE100_FREQ50'] = {
#     'policy' : '0',
#     'samples' : '100'
# }

# symParams['forest_coldstart_SAMPLE100_FREQ50'] = {
#     'policy' : '1',
#     'samples' : '100'
# }

# symParams['forest_hybrid_SAMPLE100_FREQ50'] = {
#     'policy' : '2',
#     'samples' : '100'
# }


# symParams['forest_warmstart_SAMPLE300_FREQ50'] = {
#     'policy' : '0',
#     'samples' : '300'
# }

# symParams['forest_coldstart_SAMPLE300_FREQ50'] = {
#     'policy' : '1',
#     'samples' : '300'
# }

# symParams['forest_hybrid_SAMPLE300_FREQ50'] = {
#     'policy' : '2',
#     'samples' : '300'
# }