#! /home/utils/Python-2.7.8/bin/python
import os, fnmatch, string, re, subprocess
from neovim import attach
def CompClassName(base):#,context):
    #cache = GetCacheNS('class',base)
    # if type(cache) != type(0)
    #     return cache
    # endif

    # " XXX: prevent waiting too long
    if len(base) == 0:
        return [ ]

    cache_file='/home/eash/.vim-cpan-module-cache'

#TODO create cache_file

    result = []

    #search file for cache
    fh=file(cache_file)
    for line in fh:
        if base in line:
            result.append(line.rstrip())
            print line.rstrip()

#     cal extend(classnames, s:scanClass('lib'))

    #look for all modules in lib subdirectory
    pattern='*.pm'
    for root, dirs, files in os.walk('lib'):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                name=os.path.join(root, name)
                name=name[4:-3] # remove lib/, #.pm
                name=string.replace(name,'perl5/','')
                name=string.replace(name,'/','::')
                # name=string.replace(name,'.pm','') # remove .pm
                result.append(name)
                print name

    #filter
    resultlist=[]
    for func in result:
        if func.startswith(base)
            resultlist.append(func)

    return result


# CompClassName('NV::')

# " perl builtin functions
def CompFunction(base,context)
    
    #get current functions that are in namespace, due to 'use'
    efuncs = scanCurrentExportFunction()
    #TODO
    # flist = nvim.eval(perlomni#data#p5bfunctions())
    # cal extend(flist,efuncs)
    flist=[]
    for func in efuncs:
        if func.startswith(base)
            flist.append(func)

    return flist





# " Scan export functions in current buffer
# " Return functions
def scanCurrentExportFunction():
    nvim=attach('socket',path='/tmp/nvim')
    bufname=nvim.current.buffer.name
    cache = nvim.eval("GetCacheNS('cbexf', "+bufname+")")
    # if type(l:cache) != type(0)
    #     return l:cache
    # endif

    funcs=[]

    #find the modules that are used

    for line in nvim.currentbuffer[:] # get all lines from the buffer
        match=re.search('^\s*\(use\|require\)\s+(\w+)',line)
        if match:
            #todo covert to python
            funcs.append(scanModuleExportFunctions(match.group(0)))

    return funcs
    #return SetCacheNS('cbexf',bufname('%'),funcs)

def run_perl(mtext, code):
    #todo catch error
    return subprocess.check_output(['perl', '-M'+mtext , '-e',code ])

run_perl('Moo','print @Moo::EXPORT_OK')

def scanModuleExportFunctions(class):
    # let l:cache = GetCacheNS('mef',a:class)
    # if type(l:cache) != type(0)
    #     return l:cache
    # endif

    funcs = []

    # " TODO: TOO SLOW, CACHE TO FILE!!!!
    # if exists('g:perlomni_export_functions')
    output = run_perl( a:class , printf( 'print join " ",@%s::EXPORT_OK' , a:class ))
    funcs.append( string.split(' ', output ) )
    output =run_perl( a:class , printf( 'print join " ",@%s::EXPORT' , a:class ))
    funcs.append( string.split( output ) )
    # endif
    # return SetCacheNS('mef',a:class,s:toCompHashList(funcs,a:class))
# " echo s:scanModuleExportFunctions( 'List::MoreUtils' )
# " sleep 1


