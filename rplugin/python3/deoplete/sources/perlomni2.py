# min pattern length 1
from .perl_base import Perl_base
import deoplete.util
import time
import os
import re
import subprocess
import urllib
import string
# import functools
# import operator
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
            {  # not needed as keyword completion should take care of this
                'context': '^\s*$',
                'backward': '\w+$',
                'comp': [
                    'extends', 'after', 'before', 'has',
                    'requires', 'with', 'override', 'method',
                    'super', 'around', 'inner', 'augment', 'confess', 'blessed']

            },
            {
                'only': 1,
                'context': '^use\s+[a-zA-Z0-9:]+\s+qw',
                'backward': '\w+$',
                'comp': self.CompExportFunction,
            },
            {
                'only': 1,
                'context': '^\s*(new|use)\s+(base|parent)\s+(qw.|[\'"])',
                'backward': '\w[\w\d_:]*$',
                'comp': self.CompClassName,

            },
            {
                'only': 1,
                'context': '^\s*extends\s+[\'"]',
                'backward': '[\w\d_:]+$',
                'comp': self.CompClassName,
                },
            # {  #TODO Potentailly remove, why complete function when it is already defined
            #     'only': 1,
            #     'context': '^\s*(sub|method)\s+',
            #     'backward': '\w+$',
            #     'comp': self.CompCurrentBaseFunction,
            # },

            # TODO add functions with triggers, builders, etc, add roles functions
            {
                'context': '\$(?:self|class)->',
                'backward': '\w*$',
                'only': 1,
                'comp': self.CompBufferFunction,
            },
            {
                'context': '__PACKAGE__->$',
                'backward': '\w*$',
                'only': 1,
                'comp': self.CompBufferFunction,
            },
            {
                'only': 1,
                'context': '\$\w+->$',
                'backward': '\w*$',
                'comp': self.CompObjectMethod
            },
            {
                'only': 1,
                'context': '\s*\$',
                'backward': '[A-Za-z:\d]+$',
                'comp': self.CompVariable,
            },
            {
                'only': 1,
                'context': '%',
                'backward': '\w+$',
                'comp': self.CompHashVariable,
            },
            {
                'only': 1,
                'context': '@',
                'backward': '\w+$',
                'comp': self.CompArrayVariable,
            },
            {
                'only': 1,
                'context': '&$',
                'backward': '\w+$',
                'comp': self.CompBufferFunction,
            },



            ]

    def gather_candidates(self, context):
        values = self.PerlComplete(0)
        # self.debug(type(values).__name__)
        # self.debug("size" + str(len(values)))
        # self.debug(type(values[0]).__name__)
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
            expiry = self._perlomni_cache_expiry
            last_ts = self._last_cache_ts

        if time.clock() - last_ts > expiry:
            if key in self._cache_expiry:
                self._cache_last[key] = time.clock()
            else:
                self._last_cache_ts = time.clock()
                return
        if (deoplete.util.get_simple_buffer_config(
                self.vim, 'g:perlomni_use_cache', 'g:perlomni_use_cache')):
            # if self.vim.eval('echo g:perlomni_use_cache || 1') == 1:
            return

        if key in self._cache[key]:
            return self._cache[key]
        return

    def SetCacheNSWithExpiry(self, ns, cache_key, value, exp):
        key = ns + '_' + cache_key
        self._cache[key] = value
        self._cache_expiry[key] = exp
        self._cache_last[key] = time.clock()
        return value

    def SetCacheNS(self, ns, cache_key, value):
        key = ns + "_" + cache_key
        self._cache[key] = value
        return value

# TODO
# com! PerlOmniCacheClear  :unlet g:perlomni_cache

    def CPANSourceLists(self):
        self.debug('in cpansourcelists')
        paths = [
            os.path.expanduser('~/.cpanm/sources/02packages.details.txt.gz'),
            os.path.expanduser('~/.cpanplus/02packages.details.txt.gz'),
            os.path.expanduser(
                '~/.cpan/sources/modules/02packages.details.txt.gz')]
        if self.vim.eval('exists(\'g:cpan_user_defined_sources\')'):
            paths += deoplete.util.get_simple_buffer_config(
                self.vim, 'g:cpan_user_defined_sources',
                'g:cpan_user_defined_sources')

        for f in paths:
            if os.path.isfile(f):
                return f
        #" not found
        # echo "CPAN source list not found."
        f = '~/.cpan/sources/modules/02packages.details.txt.gz'

        if not os.path.isdir(os.path.expanduser('~/.cpan/sources/modules')):
            os.mkdirs(os.path.expanduser('~/.cpan/sources/modules'))
            urllib.urlretrieve(
                'http://cpan.nctu.edu.tw/modules/02packages.details.txt.gz', f)
            return f

        # echo "Downloading CPAN source list."

        return

    def CPANParseSourceList(self, sourcefile):
        cpan_mod_cachef = os.path.expanduser('~/.vim-cpan-module-cache')
        result = []
        if not os.path.isfile(cpan_mod_cachef) or (
                os.path.getmtime(cpan_mod_cachef) < os.path.getmtime(sourcefile)):
            with open(sourcefile, 'r') as fh:
                for line in fh:
                    # TODO make sure split split works
                    (module, rest) = line.decode.split('\s', 2)
                    result.append(module)

            with open(cpan_mod_cachef) as fh:
                for module in result:
                    fh.write(module+"\n")
        else:
            with open(cpan_mod_cachef) as fh:
                for line in fh:
                    result.append(line.rstrip())
        return result

    # return list of all perl modules in a path
    def scanClass(self, path):
        cache = self.GetCacheNS('classpath', path)
        lib = []
        if cache is not None:

            return cache

        if not os.path.isdir(path):
            return []

        for root, dirs, files in os.walk(path, topdown=True, followlinks=True):
            for name in files:
                if name.endswith('.pm'):
                    name = os.path.join(root, name)
                    name = name[4:-3]  # remove lib/, #.pm
                    name = string.replace(name, 'perl5/', '')
                    name = string.replace(name, '/', '::')
                    lib.append(name)

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
            self.debug("export funcs:"+str(funcs))
        return self.SetCacheNS('mef', mClass, funcs)
        # TODO tocomphashlist doesn't look right
        # return self.SetCacheNS(
        # 'mef', mClass, self.toCompHashList(
        # funcs, mClass))

    def CompClassName(self, base, context):
        cache = self.GetCacheNS('class', self.vim.eval('getcwd()'))
        if not cache is None:
            return cache

        classnames = []
        if len(base) == 0:
            return []

        if len(self._cpan_mod_cache) != 0:
            classnames = self._cpan_mod_cache
            self.debug('mod cache exists')
        else:
            sourcefile = self.CPANSourceLists()
            classnames = self.CPANParseSourceList(sourcefile)
            self._cpan_mod_cache = classnames

        # TODO figure out how to load different libs depending on buffer
        classnames+self.scanClass('lib')

        # DEOPLETE Filters so we don't have to
        # result = self.StringFilter(classnames, base)
        return self.SetCacheNS('class', self.vim.eval('getcwd()'), classnames)

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
        # mod_pattern = '[a-zA-Z][a-zA-Z0-9:]\+'
        m = re.match('^use\s+(.*)\s+', context)
        funcs = self.scanModuleExportFunctions(m.group(1))
        # funcs = self.toCompHashList(
        #     self.scanModuleExportFunctions(
        #         m.group(1)), m.group(1))
        return funcs

    def CompCurrentBaseFunction(self, base, context):
        all_mods = self.findCurrentClassBaseClass()
        funcs = []
        for mod in all_mods:
            sublist = self.scanFunctionFromClass(mod)
            funcs += sublist
        return funcs

    def runPerlEval(self, mtext, code):
        return subprocess.check_output(
            ['perl', '-M'+mtext, "-e", code]).decode()

    #" util function for building completion hashlist
    def toCompHashList(self, mList, menu):
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
        self.debug('classfile: '+classfile)
        if classfile is None:
            return []
        # return self.scanFunctionFromSingleClassFile(
            # classfile) + self.scanFunctionFromBaseClassFile(classfile)
        return self.scanFunctionFromBaseClassFile(classfile)

    def locateClassFile(self, mClass):
        cache = self.GetCacheNS('clsfpath', mClass)
        if cache is not None:
            return cache

        paths = self.vim.options['path'].split(',')
        filepath = mClass+'.pm'
        filepath.replace('/', '::')

        output = str(
            subprocess.check_output(['perl', '-e', 'print join(",",@INC)']))
        paths += output.split(',')
        paths += 'lib'
        for path in paths:
            if os.path.isfile(path + '/' + filepath):
                return self.SetCacheNS('clsfpath', mClass, path+'/' + filepath)
        return

    def scanFunctionFromSingleClassFile(self, mfile):
        return self.grepFile('^\s*(?:sub|has|option)\s+(\w+)', mfile)

    def scanFunctionFromBaseClassFile(self, file):
        if os.path.isfile(file) == False:
            return []

        funcs = self.scanFunctionFromSingleClassFile(file)
        # self.debug('funcs: '+str(funcs))
        classes = self.baseClassFromFile(file)
        self.debug('##classes: '+str(classes))
        # TODO check for Roles
        for cls in classes:
            cache = self.GetCacheNS('classfile_funcs', cls)
            if cache is not None:
                funcs += cache
                continue

            clsfile = self.locateClassFile(cls)
            if clsfile is not None:
                self.debug('clsfile: '+clsfile)
                bfuncs = self.scanFunctionFromBaseClassFile(clsfile)
                self.SetCacheNS('classfile_funcs', cls, bfuncs)
                funcs += bfuncs
        return funcs

    def scanFunctionFromList(self):
        return self.grepBuffer('^\s*(?:sub|has|option)\s+(\w+)')

    def grepFile(self, pattern, mfile):
        ret = {}
        with open(mfile) as f:
            for line in f:
                for match in re.findall(pattern, line):
                    ret[match] = 1
        if len(ret) == 0:
            return []
        else:
            return list(ret)

    def grepBuffer(self, pattern):
        ret = {}
        for line in self.vim.current.buffer[1:]:
            for match in re.findall(pattern, line):
                ret[match] = 1
        if len(ret) == 0:
            return []
        else:
            return list(ret)

    def CompVariable(self, base, context):
        # TODO need to look at caching timeout
        cache = self.GetCacheNS('variables', 'variable')
        if cache is not None:
            return cache

        variables = []
        # TODO find way to only look in function if inside of a function
        variables = self.scanVariable()
        # self.debug("variable:"+str(variables))
        variables += self.scanArrayVariable()
        variables += self.scanHashVariable()
        return self.SetCacheNS('variables', 'variable', variables)

    def CompHashVariable(self, base, context):
        cache = self.GetCacheNS('hashvar', 'hashvar')
        if cache is not None:
            return cache
        result = self.scanHashVariable()
        return self.SetCacheNS('hashvar', 'hashvar', result)

    def CompArrayVariable(self, base, context):
        cache = self.GetCacheNS('arrayvar', base)
        if cache is not None:
            return cache
        result = self.scanArrayVariable()
        return self.SetCacheNS('arrayvar', 'arrayvar', result)

    def CompBufferFunction(self, base, context):
        # cache = self.GetCacheNS('buf_func',self.vim.current.buffer.name())
        # if cache is not None:
        #     return cache
        cache = self.GetCacheNS('buf_func_all', self.vim.current.buffer.name)
        if cache is not None:
            return cache
        else:
            funclist = self.SetCacheNS(
                'buf_func_all',
                self.vim.current.buffer.name,
                self.scanFunctionFromList())
            return funclist

        # result = filter( copy(funclist),"stridx(v:val,'".a:base."') == 0 && v:val != '".a:base."'" )
        # return
        # self.SetCacheNS('buf_func',self.vim.current.buffer.name(),result)

    def CompObjectMethod(self, base, context):
        # objvarname = matchstr(a:context,'$w\+\(->$\)\@=')
        match = re.search('\$(\w+)', context)
        objvarname = match.group(1)
        # TODO think of better caching
        # cache = self.GetCacheNS('objectMethod',objvarname)
        # if cache is not None:
        #     return cache

        classes = []
        # try to get what the package the variable is
        # " Scan from current buffer
        # " echo 'scan from current buffer' | sleep 100ms
        # TODO see if can make more python access of object
        # objvarMapping = self.vim.current.buffer.vars.get('objvarMapping')
        (lnum, lcolpos) = self.vim.current.window.cursor
        start = lnum-10
        if start < 1:
            start = 1
        lines = self.vim.current.buffer[start:lnum]
        classes = self.scanObjectVariableLines(lines, objvarname)

        funclist = []
        for cls in classes:
            funclist += self.scanFunctionFromClass(cls)
            # TODO think of better caching
            #funclist = SetCacheNS('objectMethod',objvarname,funclist)
        return funclist

    def scanArrayVariable(self):
        ret = self.grepBuffer('@(\w+)')
        return ret

    def scanVariable(self):
        ret = self.grepBuffer('\$(\w+)')
        return ret

    def scanHashVariable(self):
        ret = self.grepBuffer('\%(\w+)')
        return ret

    # look for Method that an object is
    def scanObjectVariableLines(self, lines, variable):
        p = re.compile(variable+'\s*=\s*([\w:\d_]+)->new')
        list = []
        for line in lines:
            match = p.search(line)
            if match:
                list.append(match.group(1))
        return list

    def baseClassFromFile(self, file):
        cache = self.GetCacheNS('clsf_bcls', file)
        self.debug('Getting base class from '+file)
        if cache is not None:
            return cache
        # list = split(s:system(s:vimbin.'grep-pattern.pl', a:file,
            # \ '^(?:use\s+(?:base|parent)\s+|extends\s+)(.*);'),"\n")
        list = self.grepFile('^(?:use\s+(?:base|parent)\s+|extends\s+)(.*);',file)
        classes = []
        for i in range(0, len(list)-1):
            list[i] = re.sub('^\(qw[(''"\[]|(|[''"])\s*', '', list[i],)
            list[i] = re.sub('[)''"]$', '', list[i])
            list[i] = re.sub('[,''"]', ' ', list[i],)
            classes += list[i].split('\s+')
        return self.SetCacheNS('clsf_bcls', file, classes)
