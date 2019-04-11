# Load packages and read in raw datasets

import pandas as pd
import numpy as np

dete = pd.read_csv('../dete-exit-survey-january-2014.csv',
                    na_values='Not Stated' #replace 'Not Stated' values with nulls
                  )
tafe = pd.read_csv('../tafe-employee-exit-survey-access-database-december-2013.csv',
                   encoding='iso-8859-1'
                  )

# Remove unnecessary columns

dete_updated = dete.drop(dete.columns[28:49], axis=1)
tafe_updated = tafe.drop(tafe.columns[17:66], axis=1)

# Standardize dete_updated column names

dete_updated.columns = dete_updated.columns.str.lower().str.strip().str.replace(' ', '_').str.replace('/', '_')
dete_updated.rename({'separationtype':'separation_type'}, inplace=True, axis=1)

# Standardize tafe_updated column names

pattern = r'[-\.?()/]'
tafe_updated.columns = tafe_updated.columns.str.replace(pattern, '').str.lower().str.strip()
tafe_updated.columns = tafe_updated.columns.str.replace('\s+', ' ').str.replace(' ', '_')

tafe_column_name_map = {'record_id':'id',
                        'reason_for_ceasing_employment':'separation_type',
                        'cessation_year':'cease_date',
                        'workarea':'position',
                        'employment_type_employment_type':'employment_status',
                        'contributing_factors_career_move_public_sector':'career_move_to_public_sector',
                        'contributing_factors_career_move_private_sector':'career_move_to_private_sector',
                        'contributing_factors_interpersonal_conflict':'interpersonal_conflicts',
                        'contributing_factors_job_dissatisfaction':'job_dissatisfaction',
                        'contributing_factors_maternityfamily': 'maternity_family',
                        'contributing_factors_ill_health':'ill_health',
                        'gender_what_is_your_gender':'gender',
                        'currentage_current_age': 'age',
                        'lengthofserviceoverall_overall_length_of_service_at_institute_in_years': 'length_of_service'}

tafe_updated = tafe_updated.rename(tafe_column_name_map, axis=1)
tafe_updated.drop(['institute',
                   'contributing_factors_career_move_selfemployment',
                   'contributing_factors_dissatisfaction',
                   'contributing_factors_study',
                   'contributing_factors_travel',
                   'contributing_factors_other',
                   'contributing_factors_none',
                   'classification_classification',
                   'lengthofservicecurrent_length_of_service_at_current_workplace_in_years',
                   'position'], axis=1, inplace=True)

dete_updated.drop(['role_start_date',
                   'classification',
                   'region',
                   'business_unit',
                   'dissatisfaction_with_the_department',
                   'physical_work_environment',
                   'lack_of_recognition',
                   'lack_of_job_security',
                   'work_location',
                   'employment_conditions',
                   'relocation',
                   'study_travel',
                   'traumatic_incident',
                   'work_life_balance',
                   'workload',
                   'none_of_the_above',
                   'aboriginal',
                   'torres_strait',
                   'south_sea',
                   'disability',
                   'nesb',
                   'position'], axis=1, inplace=True)

# Standardize date format of cease_date in dete - removing month from some some entries

dete_updated['cease_date'] = dete_updated['cease_date'].str.replace(r'[0-9]{2}/', '')

# Create length of service column

dete_updated['cease_date'] = pd.to_numeric(dete_updated['cease_date'])
dete_updated['length_of_service'] = dete_updated['cease_date'] - dete_updated['dete_start_date']
dete_updated.drop('dete_start_date', inplace=True, axis=1)

# Change various resignation and retirement reasons to single type - Resignation

dete_updated.loc[dete_updated['separation_type'].str.contains('Resignat'), 'separation_type'] = 'Resignation'
dete_updated.loc[dete_updated['separation_type'].str.contains('Retirement'), 'separation_type'] = 'Retirement'

# Replace 'casual' employment_status with 'contract/casual'

dete_updated.loc[dete_updated['employment_status'] == 'Casual', 'employment_status' ] = 'Contract/casual'

# Create function to convert float to categorical variable

def create_year_categories(element):
    if element == 0:
        return 'Less than 1 year'
    elif (element >= 1) & (element <= 2):
        return '1-2'
    elif (element >= 3) & (element <= 4):
        return '3-4'
    elif (element >= 5) & (element <= 6):
        return '5-6'
    elif (element >= 7) & (element <= 10):
        return '7-10'
    elif (element >= 11) & (element <= 20):
        return '11-20'
    elif element > 20:
        return 'More than 20 years'

# Convert float to categorical variable

dete_updated['length_of_service'] = dete_updated['length_of_service'].apply(create_year_categories)

# Create function to convert values to boolean

def convert_to_bool(element):
        if element == '-':
            return False
        else:
            return True

# Convert values from selected columns to boolean

columns_to_convert_to_boolean = ['career_move_to_public_sector',
                                 'career_move_to_private_sector',
                                 'ill_health',
                                 'maternity_family',
                                 'job_dissatisfaction',
                                 'interpersonal_conflicts']

for column in columns_to_convert_to_boolean:
    tafe_updated[column] = tafe_updated[column].apply(convert_to_bool)

    # Create function to convert age column of dete_updated

    def convert_age_cat(element):
        if (element == '56-60') or (element == '61 or older'):
            return '56 or older'
        else:
            return element

# Convert age column of dete_updated

dete_updated['age'] = dete_updated['age'].apply(convert_age_cat)

# Create function to update values in tafe_updated.age

def update_age_cat_spacing(element):
    tafe_age_vals = tafe_updated.age.value_counts().index[2:-1]
    if element == tafe_age_vals[0]:
        return '41-45'
    elif element == tafe_age_vals[1]:
        return '46-50'
    elif element == tafe_age_vals[2]:
        return '31-35'
    elif element == tafe_age_vals[3]:
        return '36-40'
    elif element == tafe_age_vals[4]:
        return '26-30'
    elif element == tafe_age_vals[5]:
        return '21-25'
    else:
        return element

# Update values in age column

tafe_updated['age'] = tafe_updated['age'].apply(update_age_cat_spacing)

# Create variable in each df to distinguish which df it came from

dete_updated['dataset'] = 'dete'
tafe_updated['dataset'] = 'tafe'

# Vertically concatenate dete_updated and tafe_updated

combined = pd.concat([dete_updated, tafe_updated], ignore_index=True, sort=False)

# Remove rows with missing values in any column

combined.dropna(axis=0, inplace=True)

# Write combined_data.csv file

combined.to_csv('combined_data.csv', index=False)