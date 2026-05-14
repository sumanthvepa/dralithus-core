# Python Coding Style Guidelines

When creating python code follow these style guidelines:

## Line Length

Keep lines to between 70 and 80 characters long. DO NOT
let lines be longer than 80 characters, unless it is unavoidable.

## Indentation

ALWAYS use 2 spaces for indents.


## String Quotes

ALWAYS use single quoted strings wherever possible, EXCEPT for
docstrings.

## Function Type Annotations

ALWAYS use type annotations for functions and  methods. Here is an example:

```python
  def add_numbers(a: int, b: int) -> int:
```

Notice that in the code above, both the parameters to the function and
the return value have types provided.

## Docstrings

ALWAYS add docstrings to every module class and function/method 
definition.
  * The text inside a docstring MUST be indented by two spaces from
    the surrounding triple double quotes.
    * For module docstrings at the top of a file use the following
      format:

      ```python
        """
          module_name.py: Short description of the module
        """
      ```

    * For function method docstrings, use the following format:

      ```python
        """
          Short description of the  function using imperative tense
          
          More details if necessary.

          :param param1: Description of param1
          Add more params as necessary
          :return: Description of the return type
          :raises: Describe any execptions the function might throw. One raises
                   line per execption.
        """
      ```

    * For class docstrings use the following format:

      ```python
        """
          Short description of the class

          More details if necessary.
        """
      ```
      
## Comply with PEP 8

Always write code that complies with PEP 8 guidelines except for the
indentation guideline. For that use 2 spaces as mentioned above.

## Copyleft Header

Always include the copyleft header from copyleft-template.txzt at the
top of every source file. It should be above everything except, any
shebang line, module docstring or emacs modeline. The copyleft header
should be the first thing in the file after any of those things.

## Run pylint and mypy

Always run pylint and mypy after generating code and report the 
warnings to the user. Follow their instructions on how to fix the
warnings.
