TODO
====

dictutils
---------

- autoindexing list for dictionaries. As records get added, uses a
  basic proportion-based heuristic to create subdictionaries as
  indexes over the same data. Maybe automatically does a full-scan
  option too.
- non-overwriting version of dict.update()

jsonutils
---------

* jsonl ignore blank lines
* jsonl add line number to error message

misc?
-----

- Tracking proxy. An object that always succeeds for all operations, saving the call history.
- Top/Bottom singletons (greater than and less than everything)


cliutils
--------

- progress bar
- confirmation prompt (e.g., "Question? (Y/n)")

tbutils
-------

- fold repeated frames (recursive calls)

statsutils
----------

- percentiles
- geometric mean (2 ** sum(log(a, b, ...))

funcutils
---------

#class FunctionDef(object):
#    """
#    general blocker: accept a bunch of fine-grained arguments, or just
#    accept a whole ArgSpec? or a whole signature?
#    """
#    def __init__(self, name, code, doc=None):
#        pass
