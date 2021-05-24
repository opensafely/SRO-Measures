import pandas as pd
import os
import json
import numpy as np

sentinel_measures = ["qrisk2", "asthma", "copd", "sodium", "cholesterol", "alt", "tsh", "alt", "rbc", 'hba1c', 'systolic_bp', 'medication_review']

patient_counts_dict = {}
patient_dict = {}


for file in os.listdir('output'):
    if file.startswith('input'):
        df = pd.read_feather(os.path.join('output', file))

        for measure in sentinel_measures:
            df_subset = df[df[measure]==1]
            # get unique patients
            patients = list(df_subset['patient_id'])

            if measure not in patient_dict:
                #create key
                patient_dict[measure] = patients
            
            else:
                patient_dict[measure].extend(patients)



for (key, value) in patient_dict.items():
    #get unique patients
    unique_patients = len(np.unique(patient_dict[key]))

    #add to dictionary as num(mil)
    patient_counts_dict[key] = (unique_patients/1000000)
      


with open('output/patient_count.json', 'w') as f:
    json.dump({"num_patients": patient_counts_dict}, f)
