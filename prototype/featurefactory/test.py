import glob
import os
import pandas as pd

from pyrem.features.feature_families import *
from pyrem.signal.wavelet_decomposition import decompose_signal

import pyrem as pr
from multiprocessing import Pool
import numpy as np





DATA_FILE_PATTERN= "/data/pyrem/Ellys/pkls/*.pkl"
# DATA_FILE_PATTERN= "/data/pyrem/Ellys/pkls/A*.pkl"

OUT_CSV = "/data/pyrem/Ellys/all_features.csv"
WINDOW_SIZE = 6
WINDOW_LAG = 1

N_PROCESSES = 6




def features_one_file(f):
    file_name = os.path.basename(f).split(".")[0]
    treatment, animal = file_name.split("_")
    pol = pr.polygram_from_pkl(f)

    eegs = decompose_signal(pol["EEG_parietal_cereb"], levels=[3,4,5])
    emgs = decompose_signal(pol["EMG_1"],[1,2,3,4],keep_a=False)

    pol2 = eegs.merge(emgs)
    pol2 = pol2.merge(pol["vigilance_state"])

    ##normalise
    pol2 = pol2.map_signal_channels(lambda c : (c - np.mean(c))/ np.std(c))


    feature_factory = [
                        PowerFeatures(),
                        HjorthFeatures(),
                        NonLinearFeatures(),
                        EntropyFeatures(),
                        VigilState(),]

    all_rows = []
    print "processing " + f
    old_p = 0
    for t, w in pol2.iter_window(WINDOW_SIZE, WINDOW_LAG):
        dfs = []
        for c in w.channels:
            for f in feature_factory:
                feature_vec = f.make_vector(c)
                if not feature_vec is None:
                    dfs.append(feature_vec)

        p = int(100 * t/ pol2.duration.total_seconds())
        if p != old_p:
            print f, p, "%"
            old_p = p


        row = pd.concat(dfs, axis=1)
        row.index = [t]

        all_rows.append(row)
    tmp_df = pd.concat(all_rows)

    tmp_df["animal"] = animal
    tmp_df["treatment"] = treatment



    return tmp_df

if __name__ == "__main__":

    files = glob.glob(DATA_FILE_PATTERN)

    if N_PROCESSES > 1 :
        p = Pool(N_PROCESSES)
        dfs = p.map(features_one_file, sorted(files))
    else:

        dfs = map(features_one_file, sorted(files))

    out_df = pd.concat(dfs)


    out_df.to_csv(OUT_CSV, float_format="%e")

