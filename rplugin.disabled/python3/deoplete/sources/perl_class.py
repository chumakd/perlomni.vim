#!/usr/bin/python
# -*- coding: utf-8 -*-
import deoplete.util
import re
import os
import fnmatch
import string
import subprocess
from .base import Base


class Source(Base):

    def __init__(self, vim):
        Base.__init__(self, vim)
        self.name = ('PerlClass', )
        self.mark = '[O]'
        self.rules = [
#" class name completion
# "  matches:
# "     new [ClassName]
# "     use [ClassName]
# "     use base qw(ClassName ...
# "     use base 'ClassName
                 {'context': re.compile('^use lib [\w:]*$'),
                 'backward': re.compile('([\w:]+)$'),
                 'comp': self.CompClassName},
                 {'context': re.compile('^\s*(?:requires|build_requires|test_requires)\s'),
                 'backward': re.compile('([\w:]*)$'),
                 'comp': self.CompClassName},
                 {'context': re.compile('(?:new|use)\s+[\w:]*$'),
                 'backward': re.compile('([\w:]*)$'),
                  'comp': self.CompClassName},
                 {'context': re.compile('(?:new|use)\sbase\sqw\([\w:]*$'),
                 'backward': re.compile('([\w:]*)$'),
                  'comp': self.CompClassName},
                 {'context': re.compile('(?:new|use)\sbase\s[\'"][\w:]$'),
                 'backward': re.compile('([\w:]*)$'),
                  'comp': self.CompClassName},

                 #generic class:: match
                 {'context': re.compile('[\w\d]+::[\w\d]*$'),
                 'backward': re.compile('([\w:]*)$'),
                  'comp': self.CompClassName},

                 #function completion
                 {'context': re.compile('[\s^]\w+'),
                 'backward': re.compile('([\w:]+)$'),
                  'comp': self.CompFunction},

                 ]

    def get_complete_position(self, context):
        for rule in self.rules:
            if rule['context'].match(context['input']):
                deoplete.util.debug(self.vim, 'Hi')
                m = rule['backward'].search(context['input'])
                context['completion_func'] = rule['comp']
                return (m.start() if m else -1)
        return -1
        
    def gather_candidates(self, context):
        deoplete.util.debug(self.vim, context)
        return [{'word': x} for x in context['completion_func'
                ](context['complete_str'])]

##############################
# Completion classes
##############################

    def CompClassName(self, base):  # ,context):

        # cache = GetCacheNS('class',base)
        # if type(cache) != type(0)
        #     return cache
        # endif

        # " XXX: prevent waiting too long

        if len(base) == 0:
            return []

        cache_file = '/home/eash/.vim-cpan-module-cache'

    # TODO create cache_file

        result = []

        # search file for cache

        fh = open(cache_file, 'r')
        for line in fh:
            if base in line:
                result.append(line.rstrip())

                # print line.rstrip()

    #     cal extend(classnames, s:scanClass('lib'))

        # look for all modules in lib subdirectory

        pattern = '*.pm'
        for (root, dirs, files) in os.walk('lib'):
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    name = os.path.join(root, name)
                    name = name[4:-3]  # remove lib/, #.pm
                    name = string.replace(name, 'perl5/', '')
                    name = string.replace(name, '/', '::')

                    # name=string.replace(name,'.pm','') # remove .pm

                    result.append(name)

        # filter
        # resultlist=[]
        # for func in result:
        #     if func.startswith(base)
        #         resultlist.append(func)

        return result



           # " perl builtin functions
    def CompFunction(base,context):
        
        #get current functions that are in namespace, due to 'use'
        efuncs = scanCurrentExportFunction()
        #TODO
        # flist = nvim.eval(perlomni#data#p5bfunctions())
        # cal extend(flist,efuncs)

        return efuncs

    # " Scan export functions in current buffer
    # " Return functions
    def scanCurrentExportFunction(self):
        # cache = nvim.eval("GetCacheNS('cbexf', "+bufname+")")
        # if type(l:cache) != type(0)
        #     return l:cache
        # endif

        funcs=[]

        #find the modules that are used

        for line in self.vim.currentbuffer[:]: # get all lines from the buffer
            match=re.search('^\s*\(use\|require\)\s+(\w+)',line)
            if match:
                #todo covert to python
                funcs.append(self.scanModuleExportFunctions(match.group(0)))

        return funcs
        #return SetCacheNS('cbexf',bufname('%'),funcs)

    def run_perl(mtext, code):
        #todo catch error
        return subprocess.check_output(['perl', '-M'+mtext , '-e',code ])

    def scanModuleExportFunctions(self, class_name):
        # let l:cache = GetCacheNS('mef',a:class)
        # if type(l:cache) != type(0)
        #     return l:cache
        # endif

        funcs = []

        # " TODO: TOO SLOW, CACHE TO FILE!!!!
        # if exists('g:perlomni_export_functions')
        output = run_perl( class_name, printf( 'print join " ",@%s::EXPORT_OK' , class_name ))
        funcs.append( string.split(' ', output ) )
        output =run_perl( class_name , printf( 'print join " ",@%s::EXPORT' , class_name ))
        funcs.append( string.split( output ) )
        # endif
        # return SetCacheNS('mef',a:class,s:toCompHashList(funcs,a:class))
    # " echo s:scanModuleExportFunctions( 'List::MoreUtils' )
    # " sleep 1

