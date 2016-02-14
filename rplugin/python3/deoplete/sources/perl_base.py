# ============================================================================
# FILE: base.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license  {{{
#     Permission is hereby granted, free of charge, to any person obtaining
#     a copy of this software and associated documentation files (the
#     "Software"), to deal in the Software without restriction, including
#     without limitation the rights to use, copy, modify, merge, publish,
#     distribute, sublicense, and/or sell copies of the Software, and to
#     permit persons to whom the Software is furnished to do so, subject to
#     the following conditions:
#
#     The above copyright notice and this permission notice shall be included
#     in all copies or substantial portions of the Software.
#
#     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#     OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#     MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#     IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#     CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#     TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#     SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# }}}
# ============================================================================

import re
from abc import abstractmethod
from .base import Base
import deoplete.util
import time


class Perl_base(object):

    def __init__(self, vim):
        Base.__init__(self, vim)
        self.filetypes = ['perl']
        self._last_cache_ts = time.clock()
        self._cache_expiry = {}
        self._cache_last = {}
        self._cache = {}  # g:perlomni_cache
        self._cpan_mod_cache = []  # lists of classnames for completion
        self._comps = []
        self._perlomni_cache_expiry = 30  # default value
        deoplete.util.set_default(self.vim,'g:perlomni_use_cache',1)


    def get_complete_position(self, context):
        # todo remove
        loc = self.PerlComplete(1)
        return loc


    def debug(self, expr):
        deoplete.util.debug(self.vim, expr)

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

            lcontext=context
            # lcontext = context[:-1]
            # let b:lcontext = strpart(getline('.'),0,col('.')-1)

            # " let b:pcontext
            # TODO ddefine parseParagraphhead
            paragraph_head = self.parseParagraphHead(lnum)

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
                # self.debug('bwidx:'+str(bwidx))
                lefttext = lcontext[0:bwidx]
                basetext = lcontext[bwidx:]

                self.debug('--------------------')
                self.debug('function:' + str(rule['comp']))
                self.debug('head:' + paragraph_head)
                self.debug('lefttext:' + lefttext)
                self.debug('regexp:' + rule['context'])
                self.debug('basetext:' + basetext)

                # if ( has_key( rule ,'head')
                #         \ && b:paragraph_head =~ rule.head
                #         \ && lefttext =~ rule.context )
                #     \ || ( ! has_key(rule,'head') && lefttext =~ rule.context)
                if re.match(rule['context'], lefttext):
                    self.debug('context match')
                else:
                    self.debug('context does not match')
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
                                self.debug('found contains')
                                break
                        if not found:
                            # next rule
                            self.debug('Did not find contains')
                            continue
                    if isinstance(rule['comp'], list):
                        self._comps += rule['comp']
                    else:
                        self._comps += rule['comp'](basetext, lefttext)

                    if 'only' in rule and rule['only'] == 1:
                        return bwidx

                    # save first backward index
                    if first_bwidx == -1:
                        first_bwidx = bwidx

                else:
                    self.debug('does not match')
            return first_bwidx
        else:
            return self._comps

