import pandas as pd
from pandas_schema import Column, Schema
from pandas_schema.validation import LeadingWhitespaceValidation, TrailingWhitespaceValidation, CanConvertValidation, MatchesPatternValidation, InRangeValidation, InListValidation
from io import StringIO
import schema_input

test_data = pd.read_csv('test_file.csv')

schema_input = schema_input.schema_input

schema_rows = []
for col in schema_input:
  schema_rows.append(Column(col,schema_input[col]))

schema = Schema(schema_rows)

errors = schema.validate(test_data)

for error in errors:
    print(error)

