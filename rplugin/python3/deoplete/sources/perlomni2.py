# min pattern length 1
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
            {
                'only': 1,
                'head': '^has\s+\w+',
                'context': '^\s*$',
                'backward': '\w*$',
                'comp': self.CompMooseAttribute,
            },
            {
                'only': 1,
                'head': '^with\s+',
                'context': '^\s*-$',
                'backward': '\w+$',
                'comp': ['alias', 'excludes'],
            },
            # {
            #     'context': '^\s*$',
            #     'backward': '\w+$',
            #     'comp': [
            #         'extends' , 'after' , 'before', 'has' ,
            #         'requires' , 'with' , 'override' , 'method',
            #         'super', 'around', 'inner', 'augment', 'confess' , 'blessed' ]
            #
            # },
            # {
            #     'only': 1,
            #     'context': '^use\s+[a-zA-Z0-9:]+\s+qw',
            #     'backward': '\w*$',
            #     'comp': self.CompExportFunction,
            # },
            # {
            #     'only': 1,
            #     # TODO fix <,word boundary
            #     # 'context': '\<\(new\|use\)\s\+\(\(base\|parent\)\s\+\(qw\)\?[''"(/]\)\?$' ,
            #     # 'backward': '\<[A-Z][A-Za-z0-9_:]*$',
            #     'context': '\b(new|use)\s+(base|parent)\s+(qw)?[\'"\(/])?$',
            #     'backward': '\b\w[\w\d_:]*$',
            #     'comp': self.CompClassName,
            # },
            # {
            #     'only': 1,
            #     'context': '^\s*extends\s+[\'"]$',
            #     'backward': '[\w\d_:]+$',
            #     'comp': self.CompClassName,
            # },
            # {
            #     'only': 1,
            #     'context': '^\s*(sub|method)\s+',
            #     'backward': '\w+$',
            #     'comp': self.CompCurrentBaseFunction,
            # },
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

        # TODO error - unsupported operand
        if time.localtime - last_ts > expiry:
            if key in self._cache_expiry:
                self._cache_last[key] = time.localtime
            else:
                self._last_cache_ts = time.localtime()
                return

        if self.vim.eval('echo g:perlomni_use_cache || 1') == 1:
            return

        if key in self._cache[key]:
            return self._cache[key]
        return

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
        if cache is not None:

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

    #" scan exported functions from a module.
    def scanModuleExportFunctions(self, mClass):
        cache = self.GetCacheNS('mef', mClass)
        if cache is not None:
            return cache
        funcs = []

        # TODO: TOO SLOW, CACHE TO FILE!!!!
        if self.vim.eval('exists("g:perlomni_export_functions")'):
            output = self.runPerlEval(
                mClass,
                'print join " ",@' +
                mClass +
                '::EXPORT_OK,@' +
                mClass +
                '::EXPORT')
            funcs = output.split()
        return self.SetCacheNS(
            'mef', mClass, self.toCompHashList(
                funcs, mClass))

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

    #"returns the line number of the first line in a group of lines
    def parseParagraphHead(self, fromLine):
        lnum = fromLine
        paragraph_head = self.vim.current.buffer[lnum]
        for nr in range(lnum-1, lnum-10, -1):
            line = self.vim.current.buffer[nr]
            if re.match('^\s*$', line) or re.match('^\s*#', line):
                break
            paragraph_head = line
        return paragraph_head

    def CompMooseIsa(self, base, context):
        comps = ['Int', 'Str', 'HashRef', 'HashRef[', 'Num', 'ArrayRef']
        # TODO
        # comps += self.CompClassName(base, context)
        ret = []
        for i in comps:
            ret.append("'"+i+"'")
        return ret

    def CompMooseAttribute(self, base, context):
        values = ['default', 'is', 'isa',
                  'label', 'predicate', 'metaclass', 'label',
                  'expires_after',
                  'refresh_with', 'required', 'coerce', 'does', 'required',
                  'weak_ref', 'lazy', 'auto_deref', 'trigger',
                  'handles', 'traits', 'builder', 'clearer',
                  'predicate', 'lazy_build', 'initializer', 'documentation']
        ret = []
        for i in values:
            ret.append(i+' => ')
        return ret

    def CompExportFunction(self, base, context):
        mod_pattern = '[a-zA-Z][a-zA-Z0-9:]\+'
        m = re.match('\(^use\s\+\)\@<=' + mod_pattern, context)
        funcs = self.toCompHashList(
            self.scanModuleExportFunctions(
                m.group(0)), m.group(0))
        return funcs

    def CompCurrentBaseFunction(self, base, context):
        all_mods = self.findCurrentClassBaseClass()
        funcs = []
        for mod in all_mods:
            sublist = self.scanFunctionFromClass(mod)
            funcs += sublist
        return funcs

    # TODO
    def runPerlEval(self, Mclass, string):
        return

    #" util function for building completion hashlist
    def toCompHashList(self, mList, menu):
        # return map( a:list , '{ "word": v:val , "menu": "'. a:menu .'" }' )
        # TODO verify this works
        return [{'word': val, 'menu': menu} for val in mList]

    def findCurrentClassBaseClass(self):
        all_mods = []
        for i in range(self.vim.current.line, 0, -1):
            line = self.vim.current.buffer[i]
            if re.match('^package\s+', line):
                break
            match = re.match(
                '^(?:use\s+(?:base|parent)|extends)\s+(.*)\s*;', line)
            if match:
                res = match.group(0)
                match = re.match('^qw[\'"\(\[](.*).$', res)
                args = match.group(0)
                all_mods += args.split('\s+', args)
        return all_mods

    def scanFunctionFromClass(self, mClass):
        classfile = self.locateClassFile(mClass)
        if classfile is None:
            return []
        return self.scanFunctionFromSingleClassFile(
            classfile) + self.scanFunctionFromBaseClassFile(classfile)

    def locateClassFile(self, mClass):
        cache = self.GetCacheNS('clsfpath', mClass)
        if cache is not None:
            return cache

        paths = self.vim.options['path'].split(',')
        # TODO
        # if g:perlomni_use_perlinc || &filetype != 'perl'
        # TODO
        # paths = split( s:system(g:perlomni_perl, '-e', 'print join(",",@INC)')
        # ,',')
        filepath = mClass+'.pm'
        filepath.replace('/', '::')

        paths += 'lib'
        for path in paths:
            if os.path.isfile(path + '/' + filepath):
                return self.SetCacheNS('clsfpath', mClass, path+'/' + filepath)
        return
