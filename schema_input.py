from pandas_schema.validation import LeadingWhitespaceValidation, TrailingWhitespaceValidation, CanConvertValidation, MatchesPatternValidation, InRangeValidation, InListValidation

schema_input = {
    'name':[LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
    'last_name': [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
    'age': [InRangeValidation(0, 120)],
    'sex': [InListValidation(['Male', 'Female', 'Other'])],
    'customer_id': [MatchesPatternValidation(r'\d{4}[A-Z]{4}')]
}