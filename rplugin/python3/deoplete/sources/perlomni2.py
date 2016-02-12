#min pattern length 1
from .perl_base import Perl_base
# import deoplete.util
import time
import os
import re
# import types


class Source(Perl_base):

    def __init__(self, vim):
        Perl_base.__init__(self, vim)
        self.name = 'PerlOmni_py2'
        self.mark = '[Py2]'
        self.min_pattern_length = 0
        self._rules = [
               # {'only': 1,  #TODO does not work, will not complete due to filter
                # 'context': '^\s*my\s+\$self',
                # 'backward': '\s*=\s\+shift;',
                # 'comp': [' = shift;']},
            {
                'only': 1,
                'head': '^has\s+\w+',
                'context': '\s+is\s*=>\s*$',
                'backward': '[\'"]?\w*$',
                'comp': ["'ro'", "'rw'", "'wo'"],
            },
            {
                'only': 1,
                'head': '^has\s+\w+',
                'context': '\s+(isa|does)\s*=>\s*$',
                'backward': '[\S]*$',
                'comp': self.CompMooseIsa,
            },
        ]


    def gather_candidates(self, context):
        values = self.PerlComplete(0)
        # self.debug(type(values).__name__)
        # self.debug("size" + str(len(values)))
        # self.debug(type(values[0]).__name__)
        self.debug('GATHER')
        self.debug('Candidates:'+str(values))
        if isinstance(
            values,
            list) and len(values) > 0 and isinstance(
                values[0],
                str):
            ret = []
            for x in values:
                # self.debug(type(x).__name__)
                if isinstance(x, str):
                    ret.append({'word': x})
                else:
                    ret.append(x)
                    self.debug(ret)
                    return ret
        return values

    def GetCacheNS(self, ns, cache_key):
        expiry = 0
        last_ts = 0
        key = ns+'_'+cache_key
        if key in self._cache_expiry:
            expiry = self._cache_expiry[key]
            last_ts = self._cache_last[key]
        else:
            # todo
            expiry = self._perlomni_cache_expiry
            last_ts = self._last_cache_ts

        #todo error - unsupported operand
        if time.localtime - last_ts > expiry:
            if key in self._cache_expiry:
                self._cache_last[key] = time.localtime
            else:
                self._last_cache_ts = time.localtime()
                return 0

        if self.vim.eval('echo g:perlomni_use_cache || 1') == 1:
            return 0

        if key in self._cache[key]:
            return self._cache[key]
        return 0

    def SetCacheNSWithExpiry(self, ns, cache_key, value, exp):
        key = ns + '_' + cache_key
        self._cache[key] = value
        self._cache_expiry[key] = exp
        self._cache_last[key] = time.localtime
        return value

    def SetCacheNS(self, ns, cache_key, value):
        key = ns + "_" + cache_key
        self._cache[key] = value
        return value

# TODO
# com! PerlOmniCacheClear  :unlet g:perlomni_cache

    def CPANSourceLists(self):
        # todo do in python
        return self.vim.eval('call CPANSpanSourceLists')

    # TODO
    def CPANParseSourceList(self, file):
        return self.vim.eval('call CPANParseSourceList '+file)

    # return list of all perl modules in a path
    def scanClass(self, path):
        cache = self.GetCacheNS('classpath', path)
        lib = []
        if isinstance(cache, list):
            return cache

        # TODO
        if not os.direxists(path):
            return []

        for root, dirs, files in os.walk(path, topdown=True, followlinks=True):
            for name in files:
                if name.endswith('.pm'):
                    root = root[:len(path)]  # remove initial lib
                    if root.startswith('/', beg=0):  # remove starting /
                        root = root[1:]
                        root.replace('/', '::')
                        lib.append(root+name)
                        return self.SetCacheNS('classpath', path, files)

    # TODO
    def StringFilter(self):
        return

    def CompClassName(self, base, context):
        self.debug('In CompClassName')
        # cache = self.GetCacheNS('class', base) # caching not needed
        # if type(cache) is list:
        # return cache

        classnames = []
        if len(base) == 0:
            return []

        if len(self._cpan_mod_cache) == 0:
            classnames = self._cpan_mod_cache
        else:
            sourcefile = self.CPANSourceLists()
            classnames = self.CPANParseSourceList(sourcefile)
            self._cpan_mod_cache = classnames

        # TODO figure out how to load different libs depending on buffer
        classnames.append(self.scanClass('lib'))

        # DEOPLETE Filters so we don't have to
        result = self.StringFilter(classnames, base)
        return result
    # return self.SetCacheNS('class', base, result)

    #"returns the line number of the first line in a group of lines
    def parseParagraphHead(self, fromLine):
        lnum = fromLine
        paragraph_head = self.vim.current.buffer[lnum]
        # TODO for
        for nr in range(lnum-1, lnum-10, -1):
            line = self.vim.current.buffer[nr]
            if re.match('^\s*$', line) or re.match('^\s*#', line):
                break
            paragraph_head = line
        return paragraph_head

    def CompMooseIsa(self, base, context):
        comps = ['Int', 'Str', 'HashRef', 'HashRef[', 'Num', 'ArrayRef']
        # let base = substitute(a:base,'^[''"]','','')
        comps += self.CompClassName(base, context)
        ret = []
        for i in comps:
            ret.append("'"+i+"'")
        return ret
