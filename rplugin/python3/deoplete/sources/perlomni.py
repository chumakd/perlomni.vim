from .base import Base

import deoplete.util
class Source(Base):
    def __init__(self, vim):
        Base.__init__(self,vim)
        self.name = 'PerlOmni',
        self.mark ='[O]'

    def gather_candidates(self,context):

        type=self.vim.eval("&filetype")
        if type != "perl":
            return []

        val=self.vim.eval("PerlComplete(1,'')") 
        if val < 1:
            return []
        values=self.vim.eval("PerlComplete(0,'')")
        self.vim.command("echo '"+','.join(values)+"'")

        return [{'word': x } for x in values]
