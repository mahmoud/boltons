# -*- coding: utf-8 -*-
"""Python's built-in :mod:`functools` module builds several useful
utilities on top of Python's first-class function
support. ``funcutils`` generally stays in the same vein, adding to and
correcting Python's standard metaprogramming facilities.
"""
from __future__ import print_function

import sys
import re
import inspect
import functools
import itertools
from types import MethodType, FunctionType

try:
    xrange
    make_method = MethodType
except NameError:
    # Python 3
    make_method = lambda desc, obj, obj_type: MethodType(desc, obj)
    basestring = (str, bytes)  # Python 3 compat
    _IS_PY2 = False
else:
    _IS_PY2 = True


def get_module_callables(mod, ignore=None):
    """Returns two maps of (*types*, *funcs*) from *mod*, optionally
    ignoring based on the :class:`bool` return value of the *ignore*
    callable. *mod* can be a string name of a module in
    :data:`sys.modules` or the module instance itself.
    """
    if isinstance(mod, basestring):
        mod = sys.modules[mod]
    types, funcs = {}, {}
    for attr_name in dir(mod):
        if ignore and ignore(attr_name):
            continue
        try:
            attr = getattr(mod, attr_name)
        except Exception:
            continue
        try:
            attr_mod_name = attr.__module__
        except AttributeError:
            continue
        if attr_mod_name != mod.__name__:
            continue
        if isinstance(attr, type):
            types[attr_name] = attr
        elif callable(attr):
            funcs[attr_name] = attr
    return types, funcs


def mro_items(type_obj):
    """Takes a type and returns an iterator over all class variables
    throughout the type hierarchy (respecting the MRO).

    >>> sorted(set([k for k, v in mro_items(int) if not k.startswith('__') and not callable(v)]))
    ['denominator', 'imag', 'numerator', 'real']
    """
    # TODO: handle slots?
    return itertools.chain.from_iterable(ct.__dict__.items()
                                         for ct in type_obj.__mro__)


def dir_dict(obj, raise_exc=False):
    """Return a dictionary of attribute names to values for a given
    object. Unlike ``obj.__dict__``, this function returns all
    attributes on the object, including ones on parent classes.
    """
    # TODO: separate function for handling descriptors on types?
    ret = {}
    for k in dir(obj):
        try:
            ret[k] = getattr(obj, k)
        except Exception:
            if raise_exc:
                raise
    return ret


def copy_function(orig, copy_dict=True):
    """Returns a shallow copy of the function, including code object,
    globals, closure, etc.

    >>> func = lambda: func
    >>> func() is func
    True
    >>> func_copy = copy_function(func)
    >>> func_copy() is func
    True
    >>> func_copy is not func
    True

    Args:
        orig (function): The function to be copied. Must be a
            function, not just any method or callable.
        copy_dict (bool): Also copy any attributes set on the function
            instance. Defaults to ``True``.
    """
    ret = FunctionType(orig.__code__,
                       orig.__globals__,
                       name=orig.__name__,
                       argdefs=getattr(orig, "__defaults__", None),
                       closure=getattr(orig, "__closure__", None))
    if copy_dict:
        ret.__dict__.update(orig.__dict__)
    return ret


def partial_ordering(cls):
    """Class decorator, similar to :func:`functools.total_ordering`,
    except it is used to define `partial orderings`_ (i.e., it is
    possible that *x* is neither greater than, equal to, or less than
    *y*). It assumes the presence of the ``__le__()`` and ``__ge__()``
    method, but nothing else. It will not override any existing
    additional comparison methods.

    .. _partial orderings: https://en.wikipedia.org/wiki/Partially_ordered_set

    >>> @partial_ordering
    ... class MySet(set):
    ...     def __le__(self, other):
    ...         return self.issubset(other)
    ...     def __ge__(self, other):
    ...         return self.issuperset(other)
    ...
    >>> a = MySet([1,2,3])
    >>> b = MySet([1,2])
    >>> c = MySet([1,2,4])
    >>> b < a
    True
    >>> b > a
    False
    >>> b < c
    True
    >>> a < c
    False
    >>> c > a
    False
    """
    def __lt__(self, other): return self <= other and not self >= other
    def __gt__(self, other): return self >= other and not self <= other
    def __eq__(self, other): return self >= other and self <= other

    if not hasattr(cls, '__lt__'): cls.__lt__ = __lt__
    if not hasattr(cls, '__gt__'): cls.__gt__ = __gt__
    if not hasattr(cls, '__eq__'): cls.__eq__ = __eq__

    return cls


class InstancePartial(functools.partial):
    """:class:`functools.partial` is a huge convenience for anyone
    working with Python's great first-class functions. It allows
    developers to curry arguments and incrementally create simpler
    callables for a variety of use cases.

    Unfortunately there's one big gap in its usefulness:
    methods. Partials just don't get bound as methods and
    automatically handed a reference to ``self``. The
    ``InstancePartial`` type remedies this by inheriting from
    :class:`functools.partial` and implementing the necessary
    descriptor protocol. There are no other differences in
    implementation or usage. :class:`CachedInstancePartial`, below,
    has the same ability, but is slightly more efficient.

    """
    def __get__(self, obj, obj_type):
        return make_method(self, obj, obj_type)


class CachedInstancePartial(functools.partial):
    """The ``CachedInstancePartial`` is virtually the same as
    :class:`InstancePartial`, adding support for method-usage to
    :class:`functools.partial`, except that upon first access, it
    caches the bound method on the associated object, speeding it up
    for future accesses, and bringing the method call overhead to
    about the same as non-``partial`` methods.

    See the :class:`InstancePartial` docstring for more details.
    """
    def __get__(self, obj, obj_type):
        # These assignments could've been in __init__, but there was
        # no simple way to do it without breaking one of PyPy or Py3.
        self.__name__ = None
        self.__doc__ = self.func.__doc__
        self.__module__ = self.func.__module__

        name = self.__name__
        if name is None:
            for k, v in mro_items(obj_type):
                if v is self:
                    self.__name__ = name = k
        if obj is None:
            return make_method(self, obj, obj_type)
        try:
            # since this is a data descriptor, this block
            # is probably only hit once (per object)
            return obj.__dict__[name]
        except KeyError:
            obj.__dict__[name] = ret = make_method(self, obj, obj_type)
            return ret

partial = CachedInstancePartial


# # #
# # # Function builder
# # #


def wraps(func, injected=None, **kw):
    """Modeled after the built-in :func:`functools.wraps`, this version of
    `wraps` enables a decorator to be more informative and transparent
    than ever. Use `wraps` to make your wrapper functions have the
    same name, documentation, and signature information as the inner
    function that is being wrapped.

    By default, this version of `wraps` copies the inner function's
    signature exactly, allowing seamless introspection with the
    built-in :mod:`inspect` module. In addition, the outer signature
    can be modified. By passing a list of *injected* argument names,
    those arguments will be removed from the wrapper's signature.
    """
    if injected is None:
        injected = []
    elif isinstance(injected, basestring):
        injected = [injected]

    update_dict = kw.pop('update_dict', True)
    if kw:
        raise TypeError('unexpected kwargs: %r' % kw.keys())

    fb = FunctionBuilder.from_func(func)
    for arg in injected:
        fb.remove_arg(arg)

    fb.body = 'return _call(%s)' % fb.get_invocation_str()

    def wrapper_wrapper(wrapper_func):
        execdict = dict(_call=wrapper_func, _func=func)
        fully_wrapped = fb.get_func(execdict, with_dict=update_dict)

        return fully_wrapped

    return wrapper_wrapper


class FunctionBuilder(object):
    if _IS_PY2:
        _argspec_defaults = {'args': list,
                             'varargs': lambda: None,
                             'keywords': lambda: None,
                             'defaults': lambda: None}

        @classmethod
        def _argspec_to_dict(cls, f):
            argspec = inspect.getargspec(f)
            return dict((attr, getattr(argspec, attr))
                        for attr in cls._argspec_defaults)

    else:
        _argspec_defaults = {'args': list,
                             'varargs': lambda: None,
                             'varkw': lambda: None,
                             'defaults': lambda: None,
                             'kwonlyargs': list,
                             'kwonlydefaults': dict,
                             'annotations': dict}

        @classmethod
        def _argspec_to_dict(cls, f):
            argspec = inspect.getfullargspec(f)
            return dict((attr, getattr(argspec, attr))
                        for attr in cls._argspec_defaults)

    _defaults = {'doc': str,
                 'dict': dict,
                 'module': lambda: None,
                 'body': lambda: 'pass',
                 'indent': lambda: 4}

    _defaults.update(_argspec_defaults)

    _compile_count = itertools.count()

    def __init__(self, name, **kw):
        self.name = name
        for a, default_factory in self._defaults.items():
            val = kw.pop(a, None)
            if val is None:
                val = default_factory()
            setattr(self, a, val)

        if kw:
            raise TypeError('unexpected kwargs: %r' % kw.keys())
        return

    # def get_argspec(self):  # TODO

    if _IS_PY2:
        def get_sig_str(self):
            return inspect.formatargspec(self.args, self.varargs,
                                         self.keywords, [])

        def get_invocation_str(self):
            return inspect.formatargspec(self.args, self.varargs,
                                         self.keywords, [])[1:-1]
    else:
        def get_sig_str(self):
            return inspect.formatargspec(self.args,
                                         self.varargs,
                                         self.varkw,
                                         [],
                                         self.kwonlyargs,
                                         {},
                                         self.annotations)

        _KWONLY_MARKER = re.compile(r"""
        \*     # a star
        \s*    # followed by any amount of whitespace
        ,      # followed by a comma
        \s*    # followed by any amount of whitespace
        """, re.VERBOSE)

        def get_invocation_str(self):
            kwonly_pairs = None
            formatters = {}
            if self.kwonlyargs:
                kwonly_pairs = dict((arg, arg)
                                    for arg in self.kwonlyargs)
                formatters['formatvalue'] = lambda value: '=' + value

            sig = inspect.formatargspec(self.args,
                                        self.varargs,
                                        self.varkw,
                                        [],
                                        kwonly_pairs,
                                        kwonly_pairs,
                                        {},
                                        **formatters)
            sig = self._KWONLY_MARKER.sub('', sig)
            return sig[1:-1]

    @classmethod
    def from_func(cls, func):
        # TODO: copy_body? gonna need a good signature regex.
        # TODO: might worry about __closure__?
        kwargs = {'name': func.__name__,
                  'doc': func.__doc__,
                  'module': func.__module__,
                  'dict': getattr(func, '__dict__', {})}

        kwargs.update(cls._argspec_to_dict(func))

        return cls(**kwargs)

    def get_func(self, execdict=None, add_source=True, with_dict=True):
        execdict = execdict or {}
        body = self.body or self._default_body

        tmpl = 'def {name}{sig_str}:'
        if self.doc:
            tmpl += '\n    """{doc}"""'
        tmpl += '\n{body}'

        body = _indent(self.body, ' ' * self.indent)

        name = self.name.replace('<', '_').replace('>', '_')  # lambdas
        src = tmpl.format(name=name, sig_str=self.get_sig_str(),
                          doc=self.doc, body=body)
        self._compile(src, execdict)
        func = execdict[name]

        func.__name__ = self.name
        func.__doc__ = self.doc
        func.__defaults__ = self.defaults
        if not _IS_PY2:
            func.__kwdefaults__ = self.kwonlydefaults

        if with_dict:
            func.__dict__.update(self.dict)
        func.__module__ = self.module
        # TODO: caller module fallback?

        if add_source:
            func.__source__ = src

        return func

    def get_defaults_dict(self):
        ret = dict(reversed(list(zip(reversed(self.args),
                                     reversed(self.defaults or [])))))
        return ret

    def remove_arg(self, arg_name):
        d_dict = self.get_defaults_dict()
        try:
            self.args.remove(arg_name)
        except ValueError:
            raise ValueError('arg %r not found in %s argument list: %r'
                             % (arg_name, self.name, self.args))
        d_dict.pop(arg_name, None)
        self.defaults = tuple([d_dict[a] for a in self.args if a in d_dict])
        return

    def _compile(self, src, execdict):
        filename = ('<boltons.FunctionBuilder-%d>'
                    % (next(self._compile_count),))
        try:
            code = compile(src, filename, 'single')
            exec(code, execdict)
        except Exception:
            raise
        return execdict


def _indent(text, margin, newline='\n', key=bool):
    "based on boltons.strutils.indent"
    indented_lines = [(margin + line if key(line) else line)
                      for line in text.splitlines()]
    return newline.join(indented_lines)


# end funcutils.py
