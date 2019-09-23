TODO
====

@tlog.wrap('critical', 'update campaign', verbose=True, inject_as='_act')
def update(self, _act, force=False):

Resulted in:

Traceback (most recent call last):
File "/home/mahmoud/virtualenvs/pacetrack/bin/pt", line 11, in <module>
load_entry_point('pacetrack', 'console_scripts', 'pt')()
File "/home/mahmoud/hatnote/pacetrack/pacetrack/cli.py", line 131, in main
cmd.run()
File "/home/mahmoud/projects/face/face/command.py", line 403, in run
ret = inject(wrapped, kwargs)
File "/home/mahmoud/projects/face/face/sinter.py", line 59, in inject
return f(**kwargs)
File "<sinter generated next_ d43eb353c6855dfc>", line 6, in next_
File "/home/mahmoud/hatnote/pacetrack/pacetrack/cli.py", line 138, in mw_cli_log
return next_()
File "<sinter generated next_ d43eb353c6855dfc>", line 4, in next_
File "/home/mahmoud/hatnote/pacetrack/pacetrack/cli.py", line 89, in update
return update_all(campaign_ids=posargs_, force=force, jsub=jsub, args_=args_)
File "/home/mahmoud/hatnote/pacetrack/pacetrack/cli.py", line 73, in update_all
cur_pt = load_and_update_campaign(campaign_dir, force=force)
File "/home/mahmoud/hatnote/pacetrack/pacetrack/update.py", line 622, in load_and_update_campaign
ptc.update(force=force)
File "<boltons.funcutils.FunctionBuilder-4>", line 2, in update
File "/home/mahmoud/virtualenvs/pacetrack/local/lib/python2.7/site-packages/lithoxyl/logger.py", line 298, in logged_func
return func_to_log(*a, **kw)
TypeError: update() got multiple values for keyword argument '_act'

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

- wrap_trace debug utility. Takes an object, looks at its dir, wraps
  everything callable, with a hook. Needs an enable/disable flag.
  - get/set/call/return/exception
  - __slots__
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

- dirty bit auto clears cache on property access
- geometric mean (2 ** sum(log(a, b, ...))

urlutils
--------

* improve usage of ``encoding`` arg (in parse_qsl for example)
* normalize unicode on input?
