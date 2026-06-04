import pandas as pd
import biogeme.database as db
import biogeme.biogeme as bio
from biogeme.expressions import Beta, Variable
import biogeme.models as models

# Load dataset, adjust sep and decimal to your data format
df = pd.read_csv("DataSetModel0NA6Alt.csv", sep=";", on_bad_lines='skip')

# Drop non-numeric columns if present
for col in ["Player", "Player Name", "Status"]:
    if col in df.columns:
        df = df.drop(columns=[col])

# List of columns to convert from object to float (replace comma with dot)
object_cols = [
    "nmovGK", "notmovingGK", "SR1", "SRGK1", "SR2", "SRGK2", "SR3", "SRGK3", "SR4", "SRGK4",
    "SR5", "SRGK5", "SR6", "SRGK6", "MP1", "MPGK1", "MP2", "MPGK2", "MP3", "MPGK3",
    "MP4", "MPGK4", "MP6", "MPGK6", "perc1", "perc2", "perc3", "perc4", "perc5", "perc6"
]

for col in object_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).str.replace(",", ".").replace("None", pd.NA)
        df[col] = pd.to_numeric(df[col], errors="coerce")

database = db.Database("PenaltyData", df)

Choice = Variable('Choice')

# ASC parameters (DC reference: fixed to zero)
asc_TL = Beta('asc_TL', 0, None, None, 0)
asc_TC = Beta('asc_TC', 0, None, None, 0)
asc_TR = Beta('asc_TR', 0, None, None, 0)
asc_DL = Beta('asc_DL', 0, None, None, 0)
asc_DC = Beta('asc_DC', 0, None, None, 1)  # fixed reference
asc_DR = Beta('asc_DR', 0, None, None, 0)

# Foot parameters (DC fixed)
b_foot_TL = Beta('b_foot_TL', 0, None, None, 0)
b_foot_TC = Beta('b_foot_TC', 0, None, None, 0)
b_foot_TR = Beta('b_foot_TR', 0, None, None, 0)
b_foot_DL = Beta('b_foot_DL', 0, None, None, 0)
b_foot_DC = Beta('b_foot_DC', 0, None, None, 1)  # fixed
b_foot_DR = Beta('b_foot_DR', 0, None, None, 0)

# MoveGK parameters (DC fixed)
b_moveGK_TL = Beta('b_moveGK_TL', 0, None, None, 0)
b_moveGK_TC = Beta('b_moveGK_TC', 0, None, None, 0)
b_moveGK_TR = Beta('b_moveGK_TR', 0, None, None, 0)
b_moveGK_DL = Beta('b_moveGK_DL', 0, None, None, 0)
b_moveGK_DC = Beta('b_moveGK_DC', 0, None, None, 1)  # fixed
b_moveGK_DR = Beta('b_moveGK_DR', 0, None, None, 0)

# GKS parameters (DC fixed)
b_GKS_TL = Beta('b_GKS_TL', 0, None, None, 0)
b_GKS_TC = Beta('b_GKS_TC', 0, None, None, 0)
b_GKS_TR = Beta('b_GKS_TR', 0, None, None, 0)
b_GKS_DL = Beta('b_GKS_DL', 0, None, None, 0)
b_GKS_DC = Beta('b_GKS_DC', 0, None, None, 1)  # fixed
b_GKS_DR = Beta('b_GKS_DR', 0, None, None, 0)

# IS parameters (DC fixed)
b_IS_TL = Beta('b_IS_TL', 0, None, None, 0)
b_IS_TC = Beta('b_IS_TC', 0, None, None, 0)
b_IS_TR = Beta('b_IS_TR', 0, None, None, 0)
b_IS_DL = Beta('b_IS_DL', 0, None, None, 0)
b_IS_DC = Beta('b_IS_DC', 0, None, None, 1)  # fixed
b_IS_DR = Beta('b_IS_DR', 0, None, None, 0)

# comL parameters (DC fixed)
b_comL_TL = Beta('b_comL_TL', 0, None, None, 0)
b_comL_TC = Beta('b_comL_TC', 0, None, None, 0)
b_comL_TR = Beta('b_comL_TR', 0, None, None, 0)
b_comL_DL = Beta('b_comL_DL', 0, None, None, 0)
b_comL_DC = Beta('b_comL_DC', 0, None, None, 1)  # fixed
b_comL_DR = Beta('b_comL_DR', 0, None, None, 0)

# HeiGK parameters (DC fixed)
b_HGK_TL = Beta('b_HGK_TL', 0, None, None, 0)
b_HGK_TC = Beta('b_HGK_TC', 0, None, None, 0)
b_HGK_TR = Beta('b_HGK_TR', 0, None, None, 0)
b_HGK_DL = Beta('b_HGK_DL', 0, None, None, 0)
b_HGK_DC = Beta('b_HGK_DC', 0, None, None, 1)  # fixed
b_HGK_DR = Beta('b_HGK_DR', 0, None, None, 0)

# dec parameters (DC fixed)
b_dec_TL = Beta('b_dec_TL', 0, None, None, 0)
b_dec_TC = Beta('b_dec_TC', 0, None, None, 0)
b_dec_TR = Beta('b_dec_TR', 0, None, None, 0)
b_dec_DL = Beta('b_dec_DL', 0, None, None, 0)
b_dec_DC = Beta('b_dec_DC', 0, None, None, 1)  # fixed
b_dec_DR = Beta('b_dec_DR', 0, None, None, 0)

# lp parameters (DC fixed)
b_lp_TL = Beta('b_lp_TL', 0, None, None, 0)
b_lp_TC = Beta('b_lp_TC', 0, None, None, 0)
b_lp_TR = Beta('b_lp_TR', 0, None, None, 0)
b_lp_DL = Beta('b_lp_DL', 0, None, None, 0)
b_lp_DC = Beta('b_lp_DC', 0, None, None, 1)  # fixed
b_lp_DR = Beta('b_lp_DR', 0, None, None, 0)

# latr parameters (DC fixed)
b_latr_TL = Beta('b_latr_TL', 0, None, None, 0)
b_latr_TC = Beta('b_latr_TC', 0, None, None, 0)
b_latr_TR = Beta('b_latr_TR', 0, None, None, 0)
b_latr_DL = Beta('b_latr_DL', 0, None, None, 0)
b_latr_DC = Beta('b_latr_DC', 0, None, None, 1)  # fixed
b_latr_DR = Beta('b_latr_DR', 0, None, None, 0)

# ladr parameters (DC fixed)
b_ladr_TL = Beta('b_ladr_TL', 0, None, None, 0)
b_ladr_TC = Beta('b_ladr_TC', 0, None, None, 0)
b_ladr_TR = Beta('b_ladr_TR', 0, None, None, 0)
b_ladr_DL = Beta('b_ladr_DL', 0, None, None, 0)
b_ladr_DC = Beta('b_ladr_DC', 0, None, None, 1)  # fixed
b_ladr_DR = Beta('b_ladr_DR', 0, None, None, 0)

# sr parameters only for TL and TR (TL and TR alternatives)
b_sr_TL = Beta('b_sr_TL', 0, None, None, 0)
b_sr_TR = Beta('b_sr_TR', 0, None, None, 0)

# perc generic variable (shared across all alternatives)
b_perc = Beta('b_perc', 0, None, None, 0)

# rnog parameters (DC fixed)
b_rnog_TL = Beta('b_rnog_TL', 0, None, None, 0)
b_rnog_TC = Beta('b_rnog_TC', 0, None, None, 0)
b_rnog_TR = Beta('b_rnog_TR', 0, None, None, 0)
b_rnog_DL = Beta('b_rnog_DL', 0, None, None, 0)
b_rnog_DC = Beta('b_rnog_DC', 0, None, None, 1)  # fixed
b_rnog_DR = Beta('b_rnog_DR', 0, None, None, 0)

# solsbg parameters (DC fixed)
b_solsbg_TL = Beta('b_solsbg_TL', 0, None, None, 0)
b_solsbg_TC = Beta('b_solsbg_TC', 0, None, None, 0)
b_solsbg_TR = Beta('b_solsbg_TR', 0, None, None, 0)
b_solsbg_DL = Beta('b_solsbg_DL', 0, None, None, 0)
b_solsbg_DC = Beta('b_solsbg_DC', 0, None, None, 1)  # fixed
b_solsbg_DR = Beta('b_solsbg_DR', 0, None, None, 0)

# nmovGK parameters (DC fixed)
b_nmovGK_TL = Beta('b_nmovGK_TL', 0, None, None, 0)
b_nmovGK_TC = Beta('b_nmovGK_TC', 0, None, None, 0)
b_nmovGK_TR = Beta('b_nmovGK_TR', 0, None, None, 0)
b_nmovGK_DL = Beta('b_nmovGK_DL', 0, None, None, 0)
b_nmovGK_DC = Beta('b_nmovGK_DC', 0, None, None, 1)  # fixed
b_nmovGK_DR = Beta('b_nmovGK_DR', 0, None, None, 0)

# def parameters (DC fixed)
b_def_TL = Beta('b_def_TL', 0, None, None, 0)
b_def_TC = Beta('b_def_TC', 0, None, None, 0)
b_def_TR = Beta('b_def_TR', 0, None, None, 0)
b_def_DL = Beta('b_def_DL', 0, None, None, 0)
b_def_DC = Beta('b_def_DC', 0, None, None, 1)  # fixed
b_def_DR = Beta('b_def_DR', 0, None, None, 0)

# Define variables from dataset
foot = Variable('foot')
moveGK = Variable('moveGK')
GKS = Variable('GKS')
IngSo = Variable('IngSo')
comLea = Variable('comLea')
HeiGK = Variable('HeiGK')
Dec = Variable('Dec')
lpbg = Variable('lpbg')
la3 = Variable('la3')
la6 = Variable('la6')
SRGK1 = Variable('SRGK1')
SRGK3 = Variable('SRGK3')
perc1 = Variable('perc1')
perc2 = Variable('perc2')
perc3 = Variable('perc3')
perc4 = Variable('perc4')
perc5 = Variable('perc5')
perc6 = Variable('perc6')
rnoGroup = Variable('rnoGroup')
Solsbg = Variable('Solsbg')
def_var = Variable('def')
nmovGK = Variable('nmovGK')

# Construct utility functions keyed by alternative label
V = {}

V[1] = asc_TL + b_foot_TL*foot + b_moveGK_TL*moveGK + b_GKS_TL*GKS + b_IS_TL*IngSo + b_comL_TL*comLea + \
       b_HGK_TL*HeiGK + b_dec_TL*Dec + b_lp_TL*lpbg + b_latr_TL*la3 + b_ladr_TL*la6 + b_sr_TL*SRGK1 + \
       b_perc*perc1 + b_rnog_TL*rnoGroup + b_solsbg_TL*Solsbg + b_def_TL*def_var + b_nmovGK_TL*nmovGK

V[2] = asc_TC + b_foot_TC*foot + b_moveGK_TC*moveGK + b_GKS_TC*GKS + b_IS_TC*IngSo + b_comL_TC*comLea + \
       b_HGK_TC*HeiGK + b_dec_TC*Dec + b_lp_TC*lpbg + b_latr_TC*la3 + b_ladr_TC*la6 + \
       b_perc*perc2 + b_rnog_TC*rnoGroup + b_solsbg_TC*Solsbg + b_def_TC*def_var + b_nmovGK_TC*nmovGK

V[3] = asc_TR + b_foot_TR*foot + b_moveGK_TR*moveGK + b_GKS_TR*GKS + b_IS_TR*IngSo + b_comL_TR*comLea + \
       b_HGK_TR*HeiGK + b_dec_TR*Dec + b_lp_TR*lpbg + b_latr_TR*la3 + b_ladr_TR*la6 + b_sr_TR*SRGK3 + \
       b_perc*perc3 + b_rnog_TR*rnoGroup + b_solsbg_TR*Solsbg + b_def_TR*def_var + b_nmovGK_TR*nmovGK

V[4] = asc_DL + b_foot_DL*foot + b_moveGK_DL*moveGK + b_GKS_DL*GKS + b_IS_DL*IngSo + b_comL_DL*comLea + \
       b_HGK_DL*HeiGK + b_dec_DL*Dec + b_lp_DL*lpbg + b_latr_DL*la3 + b_ladr_DL*la6 + \
       b_perc*perc4 + b_rnog_DL*rnoGroup + b_solsbg_DL*Solsbg + b_def_DL*def_var + b_nmovGK_DL*nmovGK

V[5] = asc_DC + b_foot_DC*foot + b_moveGK_DC*moveGK + b_GKS_DC*GKS + b_IS_DC*IngSo + b_comL_DC*comLea + \
       b_HGK_DC*HeiGK + b_dec_DC*Dec + b_lp_DC*lpbg + b_latr_DC*la3 + b_ladr_DC*la6 + \
       b_perc*perc5 + b_rnog_DC*rnoGroup + b_solsbg_DC*Solsbg + b_def_DC*def_var + b_nmovGK_DC*nmovGK

V[6] = asc_DR + b_foot_DR*foot + b_moveGK_DR*moveGK + b_GKS_DR*GKS + b_IS_DR*IngSo + b_comL_DR*comLea + \
       b_HGK_DR*HeiGK + b_dec_DR*Dec + b_lp_DR*lpbg + b_latr_DR*la3 + b_ladr_DR*la6 + \
       b_perc*perc6 + b_rnog_DR*rnoGroup + b_solsbg_DR*Solsbg + b_def_DR*def_var + b_nmovGK_DR*nmovGK

# Availability
av = {k: 1 for k in V}

# Define model
logprob = models.loglogit(V, av, Choice)
biogeme = bio.BIOGEME(database, logprob)
biogeme.modelName = "MNL_penalty_model"

# Estimate and export
results = biogeme.estimate()
print(results.get_estimated_parameters())
results.write_pickle()





