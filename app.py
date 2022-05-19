import streamlit as st
import pandas as pd
import io
from pandas_schema.validation import LeadingWhitespaceValidation, TrailingWhitespaceValidation, CanConvertValidation, MatchesPatternValidation, InRangeValidation, InListValidation,CustomElementValidation
from pandas_schema import Column, Schema

def main():
  if 'file_schema' not in st.session_state:
      st.session_state['file_schema'] = {}

  header = st.container()
  with header:
      st.title('''**File Schema validator**''')
      st.markdown("This tool is designed to check if a flat file complies with schema restrictions and give a data summary")

  dataset = st.container()
  with dataset:
    data_file = st.file_uploader("Upload Your CSV", type=["csv"])
    if data_file is not None:
      df = pd.read_csv(data_file,sep=",")
      st.markdown('''#### The dataset has a total of {} rows & {} Columns'''.format(df.shape[0], df.shape[1]))
      rows = st.select_slider('choose how many rows to see',range(1,len(df)))
      st.dataframe(df[0:rows])
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
  constraints = ['No Leading Whitespace','No Trailing Whitespace','Is In Range','Is In List','Matches Pattern','Max Length']
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
      errors_str.append('row: {}, column: "{}", value: "{}" {}'.format(err.row+1, err.column, err.value, err.message))
    st.text_area(label='errors',value='\n'.join(errors_str))
  else:
    st.write('No errors found')

def get_display_name_to_class_name_lookup(constraint_data):

  
  #null_validation = [CustomElementValidation(lambda d: d is not np.nan, 'this field cannot be null')]


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
  if constraint_data['name'] == 'Max Length':
    max_len_validation=CustomElementValidation(lambda x: len(x)<=constraint_data['max_chars'] ,'More than {} characters long'.format(constraint_data['max_chars']))
    return max_len_validation

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


# errors = schema.validate(data)
# errors_index_rows = [e.row for e in errors]
# data_clean = data.drop(index=errors_index_rows)
# Step 5: save the data and the errors
# We can save the errors and the clean data in two separate csv files:

# pd.DataFrame({'col':errors}).to_csv('errors.csv')
# data_clean.to_csv('clean_data.csv')