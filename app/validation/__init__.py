"""A request validator inspired by Laravel validation rules. 

The rules supported include:
1. accepted - this field must be yes, on, 1 or true
2. after:date - must be after date specified in the format YYYY-MM-DD
3. alpha - must be all alphabetic characters
4. alpha_dash - alphas and dash allowed
5. alpha_num - alpha numeric allowed
6. array - must be an array
7. before:date - must be before date specified in the format YYYY-MM-DD
8. between:min,max - 
9. boolean - true, false, 0 or 1 as well as "0" and "1"
10. confirmed - must have foo_confirmation for a field foo
11. date - must be in the format YYYY-MM-DD
12. different:field - must be different from the specified field
13. digits:value - must be numeric and must have exact length of value
14. digits_between:min,max - must be numeric and have an exact length of 
    value
15. email - must be a valid email
16. exists:table,column,... - the field under validation must exist on a 
    table
17. in:foo,bar,... - must be in the list given
18. integer - the field must be an integer
20. json - the field must be a JSON string
21. max:value -  maximum value evaluated same as the size rule
22. min:value - minimum value evaluated same as size rule
23. numeric - must be a numeric value
24. not_in:foo,bar... - field must not equal any of the values in the list
25. regex:pattern
26. required -  this field must be present
27. required_if:another_field,value,...
29. required_with:foo,bar,... - required if any of the other fields is 
    present
30. required_without:foo,bar,... - required without any of the other fields
31. same:field - the two fields must match
32. size:value - for a string, this is the length, for numeric data, value
    is the integer value. 
33. string - must be a string, empty strings are not allowed.
34. unique:table,column,except,columnId - must be unique in the given 
    table's column except the given columnId
35. url - field under validation must be a url
"""

from .validator import Validator
