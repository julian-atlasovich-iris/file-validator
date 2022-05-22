import streamlit as st
import pandas as pd
import io
from pandas_schema.validation import LeadingWhitespaceValidation, TrailingWhitespaceValidation, CanConvertValidation, MatchesPatternValidation, InRangeValidation, InListValidation,CustomElementValidation,IsDistinctValidation
from pandas_schema import Column, Schema
import matplotlib.pyplot as plt
import numpy as np

def main():
  # session variables
  if 'file_schema' not in st.session_state:
      st.session_state['file_schema'] = {}

  #header
  header = st.container()
  with header:
      st.title('''**File Schema validator**''')
      st.markdown("This tool is designed to check if a flat file complies with schema restrictions and give a data summary")

  #file uploader
  df = None
  data_file = st.file_uploader("Upload Your CSV or Excel", type=["csv","xlsx"],accept_multiple_files=False)
  if data_file is not None:
    file_type=data_file.name.split('.')[-1]
    if file_type == 'csv':
      df = pd.read_csv(data_file,sep=",") 
    elif file_type == 'xlsx':
      tabs = pd.ExcelFile(data_file).sheet_names
      sheet_name = st.selectbox('Select Sheet',tabs)
      df = pd.read_excel(data_file,sheet_name=sheet_name) 
  
  explorer = st.container()
  with explorer:
    if df is not None:
      st.markdown('''#### The dataset has a total of {} rows & {} Columns'''.format(df.shape[0], df.shape[1]))
      min_rows = 5 if 5 < len(df)+1 else 1
      #min_rows
      df.index += 2
      rows = st.select_slider('choose how many rows to see',range(min_rows,len(df)+1))
      st.dataframe(df[0:rows])
      
      st.write('---')
      col_name = st.selectbox('Column to describe',df.columns)
      #show_visuals = st.checkbox('show data visualisations')
      #if show_visuals:
      st.write("Count of unique values: {}, count of non-empty values: {}".format(df[col_name].nunique(),df[col_name].count()))
      if df[col_name].nunique() < 10:
        st.write(df[col_name].value_counts())
        st.bar_chart(df[col_name].value_counts())
      elif df[col_name].dtype == 'int64':
        st.write(df[col_name].describe())
        fig, ax = plt.subplots()
        ax.hist(df[col_name], bins="auto")
        st.pyplot(fig=plt)

  dataset = st.container()
  with dataset:
    if df is not None:
      st.write('---')
      st.write('## Add constraints')
      col_name = st.selectbox('Column',df.columns)
      constraint = get_constraint()
      btn = st.button('add constraint')
      if btn:
        if not col_name in st.session_state['file_schema']:
          st.session_state['file_schema'][col_name] = []
        if constraint not in st.session_state['file_schema'][col_name]:
          st.session_state['file_schema'][col_name].append(constraint)
      display_constraints()
      show_squema_checkbox = st.checkbox('show schema')
      if show_squema_checkbox:
        display_schema()
      if st.button('Validate'):
        validate(df)


def get_constraint():
  constraints = ['No Leading Whitespace','No Trailing Whitespace','Is In Range','Is In List','Is Unique','Matches Pattern','Max Length','No empty values']
  constraint = {}
  constraint['name'] = st.selectbox('Constraint',constraints)
  if constraint['name'] == 'Is In Range':
    constraint['low_end'] = st.number_input('low end')
    constraint['high_end'] = st.number_input('high end')
  if constraint['name'] == 'Is In List':
    constraint['options'] = st.text_input('options (comma separated)')
  if constraint['name'] == 'Matches Pattern':
    constraint['pattern'] = st.text_input('pattern (Regex)')
  if constraint['name'] == 'Max Length':
    constraint['max_chars'] = int(st.number_input('Max characters allowed'))
  return constraint

def validate(df):
  schema_rows = []
  for col in st.session_state['file_schema']:
    constraint_lst = []
    for constraint_data in st.session_state['file_schema'][col]:
      constraint = get_display_name_to_class_name_lookup(constraint_data)
      constraint_lst.append(constraint)
    schema_rows.append(Column(col,constraint_lst))
  schema = Schema(schema_rows)
  errors = schema.validate(df, columns=schema.get_column_names())
  if errors:
    errors_str = []
    for err in errors:
      value = err.value if str(err.value) != 'nan' else ' '
      errors_str.append('row: {}, column: "{}", value: "{}" {}'.format(err.row+1, err.column, value, err.message))
    st.text_area(label='errors',value='\n'.join(errors_str))
    
    #Clean file of error rows
    errors_index_rows = [e.row for e in errors]
    data_clean = df.drop(index=errors_index_rows)
    csv = data_clean.to_csv().encode('utf-8')
    st.write('Download file without error rows')
    st.download_button("Download",csv,"file.csv","text/csv",key='download-csv')
  else:
    st.write('No errors found')


  



def get_display_name_to_class_name_lookup(constraint_data):
  if constraint_data['name'] == 'No Leading Whitespace':
    return LeadingWhitespaceValidation()
  if constraint_data['name'] == 'No Trailing Whitespace':
    return TrailingWhitespaceValidation()
  if constraint_data['name'] == 'Is In Range':
    return InRangeValidation(constraint_data['low_end'],constraint_data['high_end'])
  if constraint_data['name'] == 'Is In List':
    return InListValidation(constraint_data['options'].split(','))
  if constraint_data['name'] == 'Matches Pattern':
    return MatchesPatternValidation(constraint_data['pattern'])
  if constraint_data['name'] == 'Is Unique':
    return IsDistinctValidation()
  if constraint_data['name'] == 'Max Length':
    max_len_validation=CustomElementValidation(lambda x: len(x)<=constraint_data['max_chars'] ,'More than {} characters long'.format(constraint_data['max_chars']))
    return max_len_validation
  if constraint_data['name'] == 'No empty values':    
    null_validation = CustomElementValidation(lambda d: d is not np.nan, 'this field cannot be empty')
    return null_validation

def display_constraints():
  my_display_schema = []
  for col in st.session_state['file_schema']:
    for constraint_data in st.session_state['file_schema'][col]:
      text = col + ': ' + constraint_data['name']   
      if 'low_end' in constraint_data:
        text += '(' + str(constraint_data['low_end']) + ', '
        text += str(constraint_data['high_end']) + ')'
      if 'pattern' in constraint_data:
        text += ' ' + constraint_data['pattern']
      if 'options' in constraint_data:
        text += ' ' + constraint_data['options']
      if 'max_chars' in constraint_data:
        text += ' ' + str(int(constraint_data['max_chars']))
      my_display_schema.append(text)
  st.text_area(label='constraints',value='\n'.join(my_display_schema), disabled = True)

def display_schema():
  st.write(st.session_state['file_schema'])

if __name__ == '__main__':
  main()

