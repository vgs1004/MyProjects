import pandas as pd
from biogeme import biogeme as bio
from biogeme import database as db
from biogeme.expressions import Beta, Variable, PanelLikelihoodTrajectory
from biogeme.models.nested import lognested
from biogeme.nests import OneNestForNestedLogit, NestsForNestedLogit

# ───────────────────────────────────────────────────────────
# 1) LOAD DATA + CLEAN
# ───────────────────────────────────────────────────────────
# Load dataset, adjust sep and decimal to your data format
df = pd.read_csv("DataSetModel0NA6Alt.csv", sep=";", on_bad_lines='skip')

# coerce non-numeric → NaN, then fill
df = df.apply(pd.to_numeric, errors='coerce')
df.fillna(df.mean(), inplace=True)
df.fillna(0, inplace=True)

for var in ['foot','moveGK'] + [f'perc{i}' for i in range(1,7)]:
    μ, σ = df[var].mean(), df[var].std()
    df[var] = (df[var] - μ) / (σ if σ > 0 else 1)

# Rename the choice column so it matches our Variable below
df.rename(columns={'Choice': 'CHOICE'}, inplace=True)

# ───────────────────────────────────────────────────────────
# 2) CREATE DATABASE + PANEL
# ───────────────────────────────────────────────────────────
database = db.Database("penalty", df)
database.panel("ID")



# ───────────────────────────────────────────────────────────
# 3) DEFINE VARIABLES
# ───────────────────────────────────────────────────────────

# create zero-based choice
CHOICE0 = database.define_variable('CHOICE0', Variable('CHOICE') - 1)

foot    = Variable('foot')
moveGK  = Variable('moveGK')
perc    = {i: Variable(f'perc{i}') for i in range(1,7)}
choice  = CHOICE0

# ───────────────────────────────────────────────────────────
# 4) DEFINE PARAMETERS
# ───────────────────────────────────────────────────────────
# Alternative‐specific constants (normalize DR to 0)
asc_TL = Beta('asc_TL', 0, None, None, 0)
asc_TC = Beta('asc_TC', 0, None, None, 0)
asc_TR = Beta('asc_TR', 0, None, None, 0)
asc_DL = Beta('asc_DL', 0, None, None, 0)
asc_DC = Beta('asc_DC', 0, None, None, 0)
asc_DR = Beta('asc_DR', 0, None, None, 1)

# Foot‐interaction coefficients
b_foot1 = Beta('b_foot1', 0, None, None, 0)
b_foot2 = Beta('b_foot2', 0, None, None, 0)
b_foot3 = Beta('b_foot3', 0, None, None, 1)
b_foot4 = Beta('b_foot4', 0, None, None, 0)
b_foot5 = Beta('b_foot5', 0, None, None, 0)
b_foot6 = Beta('b_foot6', 0, None, None, 1)

# GK‐movement coefficients
b_move = {i: Beta(f'b_move{i+1}', 0, None, None, 0) for i in range(6)}

# Perceived probability
b_perc = Beta('b_perc', 0.1, None, None, 0)

# Nest scale parameters (normalize Right to 1)
lambda_L = Beta('lambda_L', 0.8, 1e-6, 10, 0)
lambda_C = Beta('lambda_C', 0.8, 1e-6, 10, 0)
lambda_R = Beta('lambda_R', 0.8, 1e-6, 10, 1)    # normalized

# ───────────────────────────────────────────────────────────
# 5) UTILITY FUNCTIONS
# ───────────────────────────────────────────────────────────
V0 = asc_TL + b_foot1*foot + b_move[0]*moveGK + b_perc*perc[1]  # Top Left
V1 = asc_TC + b_foot2*foot + b_move[1]*moveGK + b_perc*perc[2]  # Top Center
V2 = asc_TR + b_foot3*foot + b_move[2]*moveGK + b_perc*perc[3]  # Top Right
V3 = asc_DL + b_foot1*foot + b_move[3]*moveGK + b_perc*perc[4]  # Bottom Left
V4 = asc_DC + b_foot2*foot + b_move[4]*moveGK + b_perc*perc[5]  # Bottom Center
V5 = asc_DR + b_foot3*foot + b_move[5]*moveGK + b_perc*perc[6]  # Bottom Right

V = {0: V0, 1: V1, 2: V2, 3: V3, 4: V4, 5: V5}

# ───────────────────────────────────────────────────────────
# 6) NEST SPECIFICATION
# ───────────────────────────────────────────────────────────
n_left   = OneNestForNestedLogit(lambda_L, [0,3], name="Left")
n_center = OneNestForNestedLogit(lambda_C, [1,4], name="Center")
n_right  = OneNestForNestedLogit(lambda_R, [2,5], name="Right")

nests = NestsForNestedLogit(
    choice_set=list(V.keys()),
    tuple_of_nests=(n_left, n_center, n_right)
)

# ───────────────────────────────────────────────────────────
# 7) PANEL‐WRAPPED LOG‐LIKELIHOOD
# ───────────────────────────────────────────────────────────
logprob  = lognested(V, None, nests, choice)
panel_ll = PanelLikelihoodTrajectory(logprob)

# ───────────────────────────────────────────────────────────
# 8) SET UP & ESTIMATE
# ───────────────────────────────────────────────────────────
biogeme = bio.BIOGEME(database, panel_ll, number_of_threads=4)
biogeme.modelName = "nested_panel_model"
results = biogeme.estimate()

# ───────────────────────────────────────────────────────────
# 9) OUTPUT
# ───────────────────────────────────────────────────────────
print(results.getEstimatedParameters())