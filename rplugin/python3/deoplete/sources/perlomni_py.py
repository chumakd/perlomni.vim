from .base import Base
import deoplete.util
import time
import os
import re
# import types


class Source(Base):

    def __init__(self, vim):
        Base.__init__(self, vim)
        self.name = 'PerlOmni_py'
        self.mark = '[Py]'
        # self.min_pattern_length = 1
        self.is_bytepos = 'True'
        self.rank = 101
        self.filetypes = ['perl']
        self._last_cache_ts = time.localtime
        self._cache_expiry = {}
        self._cache_last = {}
        self._cache = {}  # g:perlomni_cache
        self._cpan_mod_cache = []  # lists of classnames for completion
        self._comps = []
        self._perlomni_cache_expiry = 30  # default value

        self._rules = [
            # {
            #     'context': '^(requires|build_requires|test_requires)\s',
            #     'backward': '[a-zA-Z0-9:]*$',
            #     'comp': self.CompClassName,
            # },

            # {
                #     'context':'^',
                #     'backward':'sh',
                #     'comp':['shhhhhhh'],
            # },

            # {'only': 1,  #TODO does not work, will not complete due to filter
                # 'context': '^\s*my\s+\$self',
                # 'backward': '\s*=\s\+shift;',
                # 'comp': [' = shift;']},
            # {
            #     'only': 1,
            #     'head': '^has\s+\w+',
            #     'context': '\s+(isa|does)\s*=>\s*$',
            #     'backward': '[\'"]\S*$',
            #     'comp': self.CompMooseIsa,
            # },
        ]


# assume base is default
    def get_complete_position(self, context):
        # todo remove
        loc = self.PerlComplete(1)
        return loc

    def gather_candidates(self, context):
        values = self.PerlComplete(0)
        # self.debug(type(values).__name__)
        # self.debug("size" + str(len(values)))
        # self.debug(type(values[0]).__name__)
        self.debug('GATHER')
        self.debug('Candidates:'+values)
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

    def PerlComplete(self, findstart):  # , base):
        buffer = self.vim.current.buffer
        lines = buffer[1:200]
        # if ! exists('b:lines')
        #     " max 200 lines , to '$' will be very slow
        #     let b:lines = getline( 1, 200 )
        # endif

        line = self.vim.current.line
        (lnum, lcolpos) = self.vim.current.window.cursor
        # start = lcolpos - 1
        if findstart == 1:

            self._comps = []  # " will hold rules that we use on the next step
            # self._comps = self.vim.bindeval('b:comps=[]')
            # "let s_pos = s:FindSpace(star,lnum,line)
            #
            # " XXX: read lines from current buffer
            # " let b:lines   =
            context = line

            lcontext = context[:-1]
            # let b:lcontext = strpart(getline('.'),0,col('.')-1)

            # " let b:pcontext
            paragraph_head = self.parseParagraphHead(lnum)
            self.debug('I am here')

            first_bwidx = -1

            for rule in self._rules:

                # let match = matchstr( b:lcontext , rule.backward )
                match = re.search(rule['backward'], lcontext)
                if match:
                    bwidx = match.start()
                else:
                    # if backward regexp matched is empty, check if context regexp
                    # is matched ? if yes, set bwidx to length, if not , set to
                    # -1
                    if re.match(rule['context'], lcontext):
                        bwidx = len(lcontext)
                    else:
                        bwidx = -1

                # see if there is first matched index
                if first_bwidx != -1 and first_bwidx != bwidx:
                    continue

                if bwidx == -1:
                    continue

                # lefttext: context matched text
                # basetext: backward matched text
                self.debug('bwidx:'+str(bwidx))
                lefttext = lcontext[0:bwidx]
                basetext = lcontext[bwidx:]

                self.debug('function:' + str(rule['comp']))
                self.debug('head:' + paragraph_head)
                self.debug('lefttext:' + lefttext)
                self.debug('regexp:' + rule['context'])
                self.debug('basetext:' + basetext)

                # if ( has_key( rule ,'head')
                #         \ && b:paragraph_head =~ rule.head
                #         \ && lefttext =~ rule.context )
                #     \ || ( ! has_key(rule,'head') && lefttext =~ rule.context)
                if (('head' in rule and re.match(rule['head'], paragraph_head) and re.match(rule[
                    'context'], lefttext))
                    or (not ('head' in rule)
                        and re.match(rule['context'], lefttext))):

                    if 'contains' in rule:
                        # text = rule['contains']
                        found = 0
                        # check content
                        for line in lines:
                            if re.match(rule['contains'], line):
                                found = 1
                                break
                        if not found:
                            # next rule
                            continue
                    if isinstance(rule['comp'], list):
                        self.debug('competion list')
                        self._comps += rule['comp']
                    else:
                        self.debug('running function')
                        self._comps += rule['comp'](basetext, lefttext)

                    if 'only' in rule and rule['only'] == 1:
                        return bwidx

                    # save first backward index
                    if first_bwidx == -1:
                        first_bwidx = bwidx

            return first_bwidx
        else:
            return self._comps

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
        min_num=lnum-10
        if min_num <0:
            min_num=1
        paragraph_head = ''

        for nr in range(lnum-1, min_num, -1):
            line = self.vim.current.buffer[nr]
            if re.match('^\s*$', line) or re.match('^\s*#', line):
                break
            paragraph_head = line
        return paragraph_head

