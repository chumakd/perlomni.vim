import deoplete.util, re,os , fnmatch, string, subprocess
from .base import Base

class Source(Base):


    # rules={'use_lib':{}}
    def __init__(self, vim):
        Base.__init__(self,vim)
        self.name = 'PerlClass',
        self.mark ='[O]'


    def get_complete_position(self, context):
        m = re.search('use lib ', context['input'])
        if m :
            m = re.search('([\w:]+)$', context['input'])
            context['completion_func']=self.CompClassName
            return m.start() if m else -1;
        else:
            return -1



    def gather_candidates(self,context):
        deoplete.util.debug(self.vim, context)
        return [{'word': x } for x in context['completion_func'](context['complete_str'])] 




##############################
# Completion classes
##############################

    def CompClassName(self,base):#,context):
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
        fh=open(cache_file,'r')
        for line in fh:
            if base in line:
                result.append(line.rstrip())
                # print line.rstrip()

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

        #filter
        # resultlist=[]
        # for func in result:
        #     if func.startswith(base)
        #         resultlist.append(func)

        return result

